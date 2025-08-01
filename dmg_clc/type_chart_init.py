
import os
import pandas as pd
import sqlite3
from enum import Enum

# ベースディレクトリと database フォルダ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(BASE_DIR, 'database')
os.makedirs(db_dir, exist_ok=True)

db_path = os.path.join(db_dir, 'type_chart.db')

class PokemonType(Enum):
    NORMAL = "ノーマル"
    FIRE = "ほのお"
    WATER = "みず"
    ELECTRIC = "でんき"
    GRASS = "くさ"
    ICE = "こおり"
    FIGHTING = "かくとう"
    POISON = "どく"
    GROUND = "じめん"
    FLYING = "ひこう"
    PSYCHIC = "エスパー"
    BUG = "むし"
    ROCK = "いわ"
    GHOST = "ゴースト"
    DRAGON = "ドラゴン"
    DARK = "あく"
    STEEL = "はがね"
    FAIRY = "フェアリー"

type_chart_list = [t.value for t in PokemonType]

type_chart = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0, 1, 1, 0.5, 1], # ノーマル
    [1, 0.5, 0.5, 1, 2, 2, 1, 1, 1, 1, 1, 2, 0.5, 1, 0.5, 1, 2, 1], # ほのお
    [1, 2, 0.5, 1, 0.5, 1, 1, 1, 2, 1, 1, 1, 2, 1, 0.5, 1, 1, 1], # みず
    [1, 1, 2, 0.5, 0.5, 1, 1, 1, 0, 2, 1, 1, 1, 1, 0.5, 1, 1, 1], # でんき
    [1, 0.5, 2, 1, 0.5, 1, 1, 0.5, 2, 0.5, 1, 0.5, 2, 1, 0.5, 1, 0.5, 1], #くさ
    [1, 0.5, 0.5, 1, 2, 0.5, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 0.5, 1], #こおり
    [2, 1, 1, 1, 1, 2, 1, 0.5, 1, 0.5, 0.5, 0.5, 2, 0, 1, 2, 2, 0.5], #かくとう
    [1, 1, 1, 1, 2, 1, 1, 0.5, 0.5, 1, 1, 1, 0.5, 0.5, 1, 1, 0, 2], #どく
    [1, 2, 1, 2, 0.5, 1, 1, 2, 1, 0, 1, 0.5, 2, 1, 1, 1, 2, 1], #じめん
    [1, 1, 1, 0.5, 2, 1, 2, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 0.5, 1], #ひこう
    [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 0.5, 1, 1, 1, 1, 0, 0.5, 1], #エスパー
    [1, 0.5, 1, 1, 2, 1, 0.5, 0.5, 1, 0.5, 2, 1, 1, 0.5, 1, 2, 0.5, 0.5], #むし
    [1, 2, 1, 1, 1, 2, 0.5, 1, 0.5, 2, 1, 2, 1, 1, 1, 1, 0.5, 1], #いわ
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 0.5, 1, 1], #ゴースト
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 0.5, 0], #ドラゴン
    [1, 1, 1, 1, 1, 1, 0.5, 1, 1, 1, 2, 1, 1, 2, 1, 0.5, 1, 0.5], #あく
    [1, 0.5, 0.5, 0.5, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0.5, 2], #はがね
    [1, 0.5, 1, 1, 1, 1, 2, 0.5, 1, 1, 1, 1, 1, 1, 2, 2, 0.5, 1] # フェアリー 
]

df_type_chart = pd.DataFrame(type_chart, columns=type_chart_list, index=type_chart_list)
df_type_chart.reset_index(inplace=True)
df_type_chart.rename(columns={'index': 'attacker'}, inplace=True)

conn = sqlite3.connect(db_path)
df_type_chart.to_sql('type_chart', conn, if_exists='replace', index=False)
conn.close()

print(f"{db_path} にテーブルとデータを作成しました")
