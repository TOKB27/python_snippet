from pathlib import Path
import pandas as pd

# ===== 設定 =====
FOLDER_PATH = "excel_folder"   # Excelが入ったフォルダ
SHEET_NAME_KEYWORD = "対象"    # シート名に含まれる文字列
OUTPUT_CSV = "target.csv"

# G, I, J, K, L（0始まり）
USE_COLS = [6, 8, 9, 10, 11]
START_ROW = 3   # Excelの4行目
# =================


all_dfs = []

for xlsx in Path(FOLDER_PATH).rglob("*.xlsx"):
    if xlsx.name.startswith("~$"):
        continue

    try:
        excel = pd.ExcelFile(xlsx)
    except Exception as e:
        print(f"[SKIP] {xlsx}: {e}")
        continue

    for sheet in excel.sheet_names:
        if SHEET_NAME_KEYWORD not in sheet:
            continue

        df = pd.read_excel(
            xlsx,
            sheet_name=sheet,
            header=None,
            skiprows=START_ROW,
            usecols=USE_COLS,
            engine="openpyxl"
        )

        # 全列空行を除外
        df = df.dropna(how="all")

        # ★ G列（先頭列）が空の行を除外
        df = df[df.iloc[:, 0].notna()]

        all_dfs.append(df)

# CSV出力
if all_dfs:
    result = pd.concat(all_dfs, ignore_index=True)
    result.to_csv(OUTPUT_CSV, index=False, header=False, encoding="utf-8-sig")
    print("target.csv を作成しました")
else:
    print("抽出対象データがありませんでした")
