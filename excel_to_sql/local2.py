from pathlib import Path
import pandas as pd
import math

# =========================
# 設定
# =========================
INPUT_DIR = Path("./excel_files")
OUTPUT_FILE = Path("./sql_output.txt")
TARGET_SHEET_KEYWORD = "SheetName"
TABLE_NAME = "target_table"

# Modify/Delete の WHERE 条件に使うDBカラム名
WHERE_KEY_COL_A = "columnA"
WHERE_KEY_COL_B = "columnB"


# =========================
# ユーティリティ
# =========================
def is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if pd.isna(value):
        return True
    if str(value).strip() == "":
        return True
    return False


def normalize_cell(value):
    if is_empty(value):
        return None
    return value


def excel_letters():
    return [chr(code) for code in range(ord("A"), ord("Z") + 1)]


def sql_literal(value) -> str:
    """
    Python値をSQLへ直接埋め込める文字列へ変換する
    """
    if value is None:
        return "NULL"

    if isinstance(value, pd.Timestamp):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"

    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if math.isnan(value):
            return "NULL"
        if value.is_integer():
            return str(int(value))
        return str(value)

    text = str(value).replace("'", "''")
    return f"'{text}'"


# =========================
# Excel行 -> DBレコード
# =========================
def build_db_record_from_row(row_values: list):
    """
    A～Z列の値からDBレコード(dict)を構築する。
    C列は状態列なのでDB項目には含めない。
    I列とJ列の間に addF, addG, addH, addJ を追加する。
    """
    excel_map = {}
    for idx, letter in enumerate(excel_letters()):
        excel_map[letter] = normalize_cell(row_values[idx] if idx < len(row_values) else None)

    status = excel_map["C"]
    j_value = excel_map["J"]

    addF = j_value if excel_map["F"] == "X" else None
    addG = j_value if excel_map["G"] == "X" else None
    addH = j_value if excel_map["H"] == "X" else None
    addJ = j_value if excel_map["I"] == "X" else None

    record = {
        "columnA": excel_map["A"],
        "columnB": excel_map["B"],
        # C列は status のため除外
        "columnD": excel_map["D"],
        "columnE": excel_map["E"],
        "columnF": excel_map["F"],
        "columnG": excel_map["G"],
        "columnH": excel_map["H"],
        "columnI": excel_map["I"],
        "addF": addF,
        "addG": addG,
        "addH": addH,
        "addJ": addJ,
        "columnJ": excel_map["J"],
        "columnK": excel_map["K"],
        "columnL": excel_map["L"],
        "columnM": excel_map["M"],
        "columnN": excel_map["N"],
        "columnO": excel_map["O"],
        "columnP": excel_map["P"],
        "columnQ": excel_map["Q"],
        "columnR": excel_map["R"],
        "columnS": excel_map["S"],
        "columnT": excel_map["T"],
        "columnU": excel_map["U"],
        "columnV": excel_map["V"],
        "columnW": excel_map["W"],
        "columnX": excel_map["X"],
        "columnY": excel_map["Y"],
        "columnZ": excel_map["Z"],
    }

    return status, record


# =========================
# SQL生成（値埋め込み済み）
# =========================
def build_insert_sql(record: dict) -> str:
    insert_record = dict(record)
    insert_record["delete_flag"] = None

    columns = list(insert_record.keys())
    values = [sql_literal(insert_record[col]) for col in columns]

    sql = (
        f"INSERT INTO {TABLE_NAME} "
        f"({', '.join(columns)}) "
        f"VALUES ({', '.join(values)});"
    )
    return sql


def build_update_sql(record: dict) -> str:
    update_columns = [col for col in record.keys() if col not in {"columnA", "columnB"}]

    set_clause = ", ".join(
        f"{col} = {sql_literal(record[col])}" for col in update_columns
    )

    where_clause = (
        f"{WHERE_KEY_COL_A} = {sql_literal(record['columnA'])} "
        f"AND {WHERE_KEY_COL_B} = {sql_literal(record['columnB'])}"
    )

    sql = f"UPDATE {TABLE_NAME} SET {set_clause} WHERE {where_clause};"
    return sql


def build_delete_sql(record: dict) -> str:
    where_clause = (
        f"{WHERE_KEY_COL_A} = {sql_literal(record['columnA'])} "
        f"AND {WHERE_KEY_COL_B} = {sql_literal(record['columnB'])}"
    )

    sql = (
        f"UPDATE {TABLE_NAME} "
        f"SET delete_flag = 'deleted' "
        f"WHERE {where_clause};"
    )
    return sql


# =========================
# Excel処理
# =========================
def process_sheet(df: pd.DataFrame, file_name: str, sheet_name: str):
    """
    1シート分を処理して [sql, ...] を返す。
    Excelの12行目から処理開始。
    C列が空になった時点で、そのシートの処理を終了する。
    """
    statements = []
    start_row_idx = 11  # Excel上の12行目

    for row_idx in range(start_row_idx, len(df)):
        row = df.iloc[row_idx]

        # A～Z列(0～25)を取得
        row_values = [row[i] if i < len(row) else None for i in range(26)]

        # C列が空ならそのシートの処理終了
        c_value = row_values[2]
        if is_empty(c_value):
            break

        status, record = build_db_record_from_row(row_values)

        meta_comment = (
            f"-- file={file_name}, sheet={sheet_name}, excel_row={row_idx + 1}, status={status}"
        )

        if status == "New":
            statements.append(meta_comment)
            statements.append(build_insert_sql(record))
        elif status == "Modify":
            statements.append(meta_comment)
            statements.append(build_update_sql(record))
        elif status == "Delete":
            statements.append(meta_comment)
            statements.append(build_delete_sql(record))
        elif status == "NoChange":
            continue
        else:
            statements.append(
                f"-- SKIP unknown status: {status} "
                f"(file={file_name}, sheet={sheet_name}, excel_row={row_idx + 1})"
            )

        statements.append("")

    return statements


def process_excel_file(file_path: Path):
    """
    1ファイル分を処理して [sql, ...] を返す。
    """
    statements = []
    excel_file = pd.ExcelFile(file_path)

    for sheet_name in excel_file.sheet_names:
        if TARGET_SHEET_KEYWORD not in sheet_name:
            continue

        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=None,
            dtype=object
        )

        statements.extend(process_sheet(df, file_path.name, sheet_name))

    return statements


def collect_sql_statements(input_dir: Path = INPUT_DIR):
    """
    複数Excelを処理して、[sql, ...] を返す。
    """
    excel_files = []
    for pattern in ("*.xlsx", "*.xls", "*.xlsm"):
        excel_files.extend(input_dir.glob(pattern))

    all_statements = []
    for file_path in sorted(excel_files):
        all_statements.extend(process_excel_file(file_path))

    return all_statements


def write_sql_to_file(statements, output_file: Path):
    output_file.write_text("\n".join(statements), encoding="utf-8")


def main():
    statements = collect_sql_statements(INPUT_DIR)
    write_sql_to_file(statements, OUTPUT_FILE)

    print(f"SQL一覧を出力しました: {OUTPUT_FILE}")
    print(f"出力行数: {len(statements)}")

    return statements


if __name__ == "__main__":
    main()