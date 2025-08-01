import pandas as pd
import sqlite3

# Excel ファイルのパス
excel_file = "data/skill.xlsx"

# SQLite データベースファイル名
db_file = "database/skill.db"

# Excel ファイルを読み込み
xls = pd.ExcelFile(excel_file)

# SQLite に接続（なければ作成されます）
conn = sqlite3.connect(db_file)

# 各シートをテーブルとしてDBに保存
for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name)
    # テーブル名はシート名を使用
    df.to_sql(sheet_name, conn, index=False, if_exists='replace')
    print(f"Sheet '{sheet_name}' をテーブルに追加しました。")

conn.close()
print(f"データベース '{db_file}' が作成されました。")
