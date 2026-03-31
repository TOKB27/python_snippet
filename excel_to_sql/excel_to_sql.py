import os
import io
import math
import logging
from collections import defaultdict

import boto3
import pandas as pd
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

TARGET_SHEET_KEYWORD = "SheetName"
TABLE_NAME = "target_table"

# Modify/Delete の WHERE 条件に使うDBカラム名
WHERE_KEY_COL_A = "columnA"
WHERE_KEY_COL_B = "columnB"


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


def process_sheet(df: pd.DataFrame, file_name: str, sheet_name: str):
    """
    1シート分を処理して [(sql, params), ...] を返す。
    Excelの12行目から処理開始。
    C列が空になった時点で、そのシートの処理を終了する。
    """
    statements = []
    start_row_idx = 11  # Excel上の12行目

    for row_idx in range(start_row_idx, len(df)):
        row = df.iloc[row_idx]

        # A～Z列(0～25)
        row_values = [row[i] if i < len(row) else None for i in range(26)]

        # C列が空なら、そのシートの処理終了
        c_value = row_values[2]
        if is_empty(c_value):
            logger.info(
                "Stop reading sheet because column C is empty. file=%s sheet=%s excel_row=%s",
                file_name, sheet_name, row_idx + 1
            )
            break

        status, record = build_db_record_from_row(row_values)

        if status == "New":
            statements.append(build_insert_sql_and_params(record))
        elif status == "Modify":
            statements.append(build_update_sql_and_params(record))
        elif status == "Delete":
            statements.append(build_delete_sql_and_params(record))
        elif status == "NoChange":
            continue
        else:
            logger.warning(
                "Skip unknown status. file=%s sheet=%s excel_row=%s status=%s",
                file_name, sheet_name, row_idx + 1, status
            )

    return statements


def read_excel_from_s3(bucket: str, key: str) -> io.BytesIO:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    body = response["Body"].read()
    return io.BytesIO(body)


def process_excel_file_from_s3(bucket: str, key: str):
    """
    S3上の1ファイルを処理して [(sql, params), ...] を返す。
    """
    statements = []
    file_obj = read_excel_from_s3(bucket, key)

    excel_file = pd.ExcelFile(file_obj)

    for sheet_name in excel_file.sheet_names:
        if TARGET_SHEET_KEYWORD not in sheet_name:
            continue

        df = pd.read_excel(
            file_obj,
            sheet_name=sheet_name,
            header=None,
            dtype=object
        )

        # read_excel後に同じ BytesIO を再利用すると位置が進むため、
        # シートごとに読み直せるよう最初から開き直す
        # ExcelFileオブジェクトから読む形に変更
        df = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            header=None,
            dtype=object
        )

        sheet_statements = process_sheet(df, key, sheet_name)
        statements.extend(sheet_statements)

    return statements


def list_excel_keys(bucket: str, prefix: str):
    """
    S3FILEPATH 配下の Excel ファイル一覧を返す。
    """
    keys = []
    continuation_token = None

    while True:
        kwargs = {
            "Bucket": bucket,
            "Prefix": prefix,
            "MaxKeys": 1000,
        }
        if continuation_token:
            kwargs["ContinuationToken"] = continuation_token

        response = s3_client.list_objects_v2(**kwargs)

        for item in response.get("Contents", []):
            key = item["Key"]
            lower_key = key.lower()

            if lower_key.endswith(".xlsx") or lower_key.endswith(".xls") or lower_key.endswith(".xlsm"):
                keys.append(key)

        if response.get("IsTruncated"):
            continuation_token = response.get("NextContinuationToken")
        else:
            break

    return keys


def collect_sql_statements_from_s3(bucket: str, prefix: str):
    """
    S3配下の複数Excelを処理し、[(sql, params), ...] を返す。
    """
    keys = list_excel_keys(bucket, prefix)
    logger.info("Excel files found: %s", len(keys))

    all_statements = []
    for key in keys:
        logger.info("Processing file: s3://%s/%s", bucket, key)
        all_statements.extend(process_excel_file_from_s3(bucket, key))

    return all_statements


def group_statements_by_sql(statements):
    """
    [(sql, params), ...] を
    {
      sql1: [params1, params2, ...],
      sql2: [params3, params4, ...]
    }
    にまとめる。
    """
    grouped = defaultdict(list)
    for sql, params in statements:
        grouped[sql].append(params)
    return grouped


def get_db_connection():
    """
    DB接続。
    実際の接続情報は環境変数から取得する想定。
    例:
      DB_HOST
      DB_PORT
      DB_NAME
      DB_USER
      DB_PASSWORD
    """
    host = os.environ["DB_HOST"]
    port = int(os.environ.get("DB_PORT", "5432"))
    dbname = os.environ["DB_NAME"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
    return conn


def execute_statements_efficiently(connection, statements):
    """
    同じSQLごとにまとめて executemany する。
    実際のSQL実行箇所はコメントアウトしている。
    """
    grouped = group_statements_by_sql(statements)

    for sql, params_list in grouped.items():
        logger.info("Prepared SQL batch. sql=%s count=%s", sql, len(params_list))

        # 実際に実行する場合はコメントアウトを外す
        # with connection.cursor() as cursor:
        #     cursor.executemany(sql, params_list)

    # 実際にコミットする場合はコメントアウトを外す
    # connection.commit()


def lambda_handler(event, context):
    bucket = os.environ["S3BAKETNAME"]
    prefix = os.environ["S3FILEPATH"]

    logger.info("Start Lambda. bucket=%s prefix=%s", bucket, prefix)

    statements = collect_sql_statements_from_s3(bucket, prefix)

    logger.info("Total SQL statements: %s", len(statements))

    # DB実行イメージ
    # conn = None
    # try:
    #     conn = get_db_connection()
    #     execute_statements_efficiently(conn, statements)
    # except Exception:
    #     if conn:
    #         conn.rollback()
    #     logger.exception("Failed to execute SQL")
    #     raise
    # finally:
    #     if conn:
    #         conn.close()

    return {
        "statusCode": 200,
        "message": "Processed successfully",
        "statementCount": len(statements),
        "sample": [
            {
                "sql": sql,
                "params": list(params)
            }
            for sql, params in statements[:3]
        ],
    }