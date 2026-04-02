from pathlib import Path
from collections import defaultdict
import pandas as pd
import math
import json

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


def to_serializable(value):
    """テキスト出力用にJSONシリアライズ可能な値へ変換"""
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value


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
# SQL生成
# =========================
def build_insert_sql_and_params(record: dict):
    insert_record = dict(record)
    insert_record["delete_flag"] = None

    columns = list(insert_record.keys())
    sql = (
        f"INSERT INTO {TABLE_NAME} "
        f"({', '.join(columns)}) "
        f"VALUES ({', '.join(['%s'] * len(columns))});"
    )
    params = tuple(insert_record[col] for col in columns)
    return sql, params


def build_update_sql_and_params(record: dict):
    update_columns = [col for col in record.keys() if col not in {"columnA", "columnB"}]

    sql = (
        f"UPDATE {TABLE_NAME} "
        f"SET {', '.join(f'{col} = %s' for col in update_columns)} "
        f"WHERE {WHERE_KEY_COL_A} = %s AND {WHERE_KEY_COL_B} = %s;"
    )

    params = tuple(record[col] for col in update_columns) + (
        record["columnA"],
        record["columnB"],
    )
    return sql, params


def build_delete_sql_and_params(record: dict):
    sql = (
        f"UPDATE {TABLE_NAME} "
        f"SET delete_flag = %s "
        f"WHERE {WHERE_KEY_COL_A} = %s AND {WHERE_KEY_COL_B} = %s;"
    )
    params = ("deleted", record["columnA"], record["columnB"])
    return sql, params


# =========================
# Excel処理
# =========================
def process_sheet(df: pd.DataFrame, file_name: str, sheet_name: str):
    """
    1シート分を処理して [(sql, params, meta), ...] を返す。
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

        meta = {
            "file": file_name,
            "sheet": sheet_name,
            "excel_row": row_idx + 1,
            "status": status,
        }

        if status == "New":
            sql, params = build_insert_sql_and_params(record)
            statements.append((sql, params, meta))
        elif status == "Modify":
            sql, params = build_update_sql_and_params(record)
            statements.append((sql, params, meta))
        elif status == "Delete":
            sql, params = build_delete_sql_and_params(record)
            statements.append((sql, params, meta))
        elif status == "NoChange":
            continue
        else:
            # 想定外ステータスはスキップ
            continue

    return statements


def process_excel_file(file_path: Path):
    """
    1ファイル分を処理して [(sql, params, meta), ...] を返す。
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
    複数Excelを処理して、[(sql, params, meta), ...] を返す。
    """
    excel_files = []
    for pattern in ("*.xlsx", "*.xls", "*.xlsm"):
        excel_files.extend(input_dir.glob(pattern))

    all_statements = []
    for file_path in sorted(excel_files):
        all_statements.extend(process_excel_file(file_path))

    return all_statements


# =========================
# 出力
# =========================
def write_statements_to_file(statements, output_file: Path):
    """
    SQL一覧をテキストファイルへ出力する。
    """
    output_lines = []

    output_lines.append(f"total_statements: {len(statements)}")
    output_lines.append("")

    for idx, (sql, params, meta) in enumerate(statements, start=1):
        serializable_params = [to_serializable(v) for v in params]

        output_lines.append(f"--- statement {idx} ---")
        output_lines.append(f"file      : {meta['file']}")
        output_lines.append(f"sheet     : {meta['sheet']}")
        output_lines.append(f"excel_row : {meta['excel_row']}")
        output_lines.append(f"status    : {meta['status']}")
        output_lines.append(f"sql       : {sql}")
        output_lines.append(
            "params    : " + json.dumps(serializable_params, ensure_ascii=False)
        )
        output_lines.append("")

    output_file.write_text("\n".join(output_lines), encoding="utf-8")


def write_grouped_summary_to_file(statements, output_file: Path):
    """
    同じSQLごとの件数サマリを別ファイルに出したい場合に使う。
    """
    grouped = defaultdict(list)
    for sql, params, meta in statements:
        grouped[sql].append((params, meta))

    summary_file = output_file.with_name(output_file.stem + "_summary.txt")

    lines = []
    lines.append(f"sql_pattern_count: {len(grouped)}")
    lines.append("")

    for idx, (sql, values) in enumerate(grouped.items(), start=1):
        lines.append(f"--- sql pattern {idx} ---")
        lines.append(f"count: {len(values)}")
        lines.append(f"sql  : {sql}")
        lines.append("")

    summary_file.write_text("\n".join(lines), encoding="utf-8")


def main():
    statements = collect_sql_statements(INPUT_DIR)
    write_statements_to_file(statements, OUTPUT_FILE)
    write_grouped_summary_to_file(statements, OUTPUT_FILE)

    print(f"SQL一覧を出力しました: {OUTPUT_FILE}")
    print(f"件数: {len(statements)}")

    return statements


if __name__ == "__main__":
    statements = main()