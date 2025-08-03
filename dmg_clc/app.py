from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import sqlite3
import math

app = Flask(__name__)
app.secret_key = 'secret'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(BASE_DIR, 'database')
os.makedirs(db_dir, exist_ok=True)

db_path = os.path.join(db_dir, 'data.db')
type_chart_db_path = os.path.join(db_dir, 'type_chart.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def kirisute(num):
    num_f = (num * 10) % 10  # 小数第1位を取り出す
    if num_f <= 5:
        num = math.floor(num)
    else:
        num = math.ceil(num)
    return num

def kirisute_calc(num1,num2):
    num = num1 * num2
    num_f = (num * 10) % 10  # 小数第1位を取り出す
    if num_f <= 5:
        num = math.floor(num)
    else:
        num = math.ceil(num)
    return num

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    type1 = db.Column(db.String(50))
    type2 = db.Column(db.String(50))
    property1 = db.Column(db.String(50))
    property2 = db.Column(db.String(50))
    property3 = db.Column(db.String(50))
    property4 = db.Column(db.String(50))
    hp = db.Column(db.Integer)
    at = db.Column(db.Integer)
    bl = db.Column(db.Integer)
    co = db.Column(db.Integer)
    de = db.Column(db.Integer)
    sp = db.Column(db.Integer)

def init_db_from_csv():
    if not os.path.exists(db_path):
        db.create_all()
        csv_path = os.path.join(BASE_DIR, 'data', 'data.csv')
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=['Hp'])
        df['id'] = df['id'].astype(int)
        df['Hp'] = df['Hp'].astype(int)
        df['At'] = df['At'].astype(int)
        df['Bl'] = df['Bl'].astype(int)
        df['Co'] = df['Co'].astype(int)
        df['De'] = df['De'].astype(int)
        df['Sp'] = df['Sp'].astype(int)

        for _, row in df.iterrows():
            item = Item(
                id=row['id'], name=row['name'], type1=row['type1'], type2=row['type2'],
                property1=row['property1'], property2=row['property2'],
                property3=row['property3'], property4=row['property4'],
                hp=row['Hp'], at=row['At'], bl=row['Bl'], co=row['Co'], de=row['De'], sp=row['Sp']
            )
            db.session.add(item)
        db.session.commit()
        print("DB initialized from CSV")

class SkillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    category = db.Column(db.String(50))
    power = db.Column(db.Integer)
    dynamax = db.Column(db.Integer)
    accuracy = db.Column(db.Integer)
    pp = db.Column(db.Integer)
    direct = db.Column(db.String(10))
    protect = db.Column(db.String(10))
    target = db.Column(db.String(20))
    description = db.Column(db.Text)

def init_db_from_excel():
    db_path = os.path.join(BASE_DIR, 'database', 'skill.db')
    if not os.path.exists(db_path):
        db.create_all()
        excel_path = os.path.join(BASE_DIR, 'data', 'skill.xlsx')

        # シート名を指定
        df = pd.read_excel(excel_path, sheet_name='技データリスト')

        # 欠損が多い列があるなら除外も検討（例: 威力や命中など）
        # df = df.dropna(subset=['威力'])

        # 数値として扱いたい列を整数型に変換（必要なら）
        df['威力'] = pd.to_numeric(df['威力'], errors='coerce').fillna(0).astype(int)
        df['ダイマックス'] = pd.to_numeric(df['ダイマックス'], errors='coerce').fillna(0).astype(int)
        df['命中'] = pd.to_numeric(df['命中'], errors='coerce').fillna(0).astype(int)
        df['PP'] = pd.to_numeric(df['PP'], errors='coerce').fillna(0).astype(int)

        for _, row in df.iterrows():
            item = SkillItem(
                name=row['名前'],
                type=row['タイプ'],
                category=row['分類'],
                power=row['威力'],
                dynamax=row['ダイマックス'],
                accuracy=row['命中'],
                pp=row['PP'],
                direct=row['直接'],
                protect=row['守る'],
                target=row['対象'],
                description=row['説明']
            )
            db.session.add(item)
        db.session.commit()
        print("Excel用DBを初期化しました")


@app.route('/', methods=['GET', 'POST'])
def index():
    search_name_At = ''
    search_name_Bl = ''
    search_name_skill = ''
    lv_at = lv_bl = 50  # レベル

    # 初期値を設定
    char_At = None
    char_Bl = None
    skill_type = None # 物理 or 特殊
    types = None # タイプ
    power = 0
    at_calc_value1 = bl_calc_value1 = None
    weather = field = None

    # 能力値なども初期値
    base_hp = 1
    not_max = None
    not_skill_name = None
    at_power = co_power = bl_power = de_power = 0
    hp_indv = at_indv = co_indv = bl_indv = de_indv = 0
    hp_eff = at_eff = co_eff = bl_eff = de_eff = 0
    at_lank = co_lank = bl_lank = de_lank = 0
    hp_real = at_real = co_real = bl_real = de_real = 0
    at_nature = co_nature = bl_nature = de_nature = 0
    at_dynamax = bl_dynamax = None
    at_dynamax_level = bl_dynamax_level = 0
    at_terastal = bl_terastal = None
    at_teras_type = bl_teras_type = None

    total_dmg = min_dmg = max_dmg = None
    min_hp = max_hp = None
    par = None
    par_ram = None
    kill = 5
    par_min = par_max = None

    type1 = type2 = type3 = type4 = None
    property1 = property2 = property3 = None
    match1 = match2 = None

    multiple = multiple2 = 1

    hosei_at = hosei_co = hosei_bl = hosei_de = 1.0
    hosei_pow = hosei_dmg = 1.0

    last_at = last_co = last_bl = last_de = 0

    choise = None

    type_match = None
    matching_types = []

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'search_at':
            search_name_At = request.form.get('search_name_At', '').strip()
            session['search_name_At'] = search_name_At  # セッションに保存
            
            if search_name_At:
                item_at = Item.query.filter(Item.name.like(f'%{search_name_At}%')).first()
                if item_at:
                    at_power = item_at.at or 1
                    co_power = item_at.co or 1
                    type1 = item_at.type1
                    type2 = item_at.type2
                    property1 = item_at.property1
                    property2 = item_at.property2
                    property3 = item_at.property3

                    session['at_power'] = at_power
                    session['co_power'] = co_power
                    session['type1'] = type1
                    session['type2'] = type2
                    session['property1'] = property1
                    session['property2'] = property2
                    session['property3'] = property3

        elif action == 'search_bl':
            search_name_Bl = request.form.get('search_name_Bl', '').strip()
            session['search_name_Bl'] = search_name_Bl  # セッションに保存
            if search_name_Bl:
                item_bl = Item.query.filter(Item.name.like(f'%{search_name_Bl}%')).first()
                if item_bl:
                    base_hp = item_bl.hp or 1
                    bl_power = item_bl.bl or 1
                    de_power = item_bl.de or 1
                    type3 = item_bl.type1
                    type4 = item_bl.type2
                    
                    session['base_hp'] = base_hp
                    session['bl_power'] = bl_power
                    session['de_power'] = de_power
                    session['type3'] = type3
                    session['type4'] = type4

        # elif action == 'search_skill':
        #     search_name_skill = request.form.get('search_name_skill', '').strip()
        #     session['search_name_skill'] = search_name_skill  # セッションに保存
            
        #     if search_name_skill:
        #         item_sk = Item.query.filter(Item.name.like(f'%{search_name_skill}%')).first()
        #         if item_sk:
        #             power = item_sk.power or 1
        #             accuracy = item_sk.accuracy or 1
        #             type = item_sk.type
        #             skill_type = item_sk.category
        #             dynamax = item_sk.dynamax
        #             direct = item_sk.direct
        #             protect = item_sk.protect

        #              # セッションに保存（キー名は用途に応じて自由に決めてOK）
        #             session['power'] = power # 威力
        #             session['accuracy'] = accuracy
        #             session['type'] = type # タイプ
        #             session['category'] = skill_type # 物理特殊
        #             session['dynamax'] = dynamax
        #             session['direct'] = direct
        #             session['protect'] = protect
                    
        elif action == 'calculate':
            # base_hp = int(request.form.get('base_hp', session.get('base_hp', 1)) or 1)
            base_hp = session.get('base_hp')

            # type = request.form.get('type', '')
            types = request.form.get('types', session.get('types', ''))
            session['types'] = types
            skill_type = request.form.get('skill_type', '')
            power = int(request.form.get('power', 0) or 0)
            
            # typeなどはセッションから取り出す
            type1 = session.get('type1')
            type2 = session.get('type2')
            type3 = session.get('type3')
            type4 = session.get('type4')
            property1 = session.get('property1')
            property2 = session.get('property2')
            property3 = session.get('property3')

            at_dynamax = request.form.get('at_dynamax') == 'on'
            bl_dynamax = request.form.get('bl_dynamax') == 'on'
            at_dynamax_level = int(request.form.get('at_dynamax_level', session.get('at_dynamax_level', 0)) or 0)
            bl_dynamax_level = int(request.form.get('bl_dynamax_level', session.get('bl_dynamax_level', 0)) or 0)

            at_terastal = request.form.get('at_terastal') == 'on'
            bl_terastal = request.form.get('bl_terastal') == 'on'
            at_teras_type = request.form.get('at_teras_type', session.get('at_teras_type', ''))
            bl_teras_type = request.form.get('bl_teras_type', session.get('bl_teras_type', ''))

            not_max = request.form.get('not_max') == 'on'
            
            char_At = request.form.get('char_At', '')
            char_Bl = request.form.get('char_Bl', '')

            at_power = int(request.form.get('at_power', session.get('at_power', 1)) or 1)
            co_power = int(request.form.get('co_power', session.get('co_power', 1)) or 1)
            bl_power = int(request.form.get('bl_power', session.get('bl_power', 1)) or 1)
            de_power = int(request.form.get('de_power', session.get('de_power', 1)) or 1)

            hp_indv = int(request.form.get('hp_indv', 0) or 0)
            at_indv = int(request.form.get('at_indv', 0) or 0)
            co_indv = int(request.form.get('co_indv', 0) or 0)
            bl_indv = int(request.form.get('bl_indv', 0) or 0)
            de_indv = int(request.form.get('de_indv', 0) or 0)

            hp_eff = int(request.form.get('hp_eff', 0) or 0)
            at_eff = int(request.form.get('at_eff', 0) or 0)
            co_eff = int(request.form.get('co_eff', 0) or 0)
            bl_eff = int(request.form.get('bl_eff', 0) or 0)
            de_eff = int(request.form.get('de_eff', 0) or 0)

            at_lank = int(request.form.get('at_lank', session.get('at_lank', 0)) or 0)
            co_lank = int(request.form.get('co_lank', session.get('co_lank', 0)) or 0)
            bl_lank = int(request.form.get('bl_lank', session.get('bl_lank', 0)) or 0)
            de_lank = int(request.form.get('de_lank', session.get('de_lank', 0)) or 0)

            at_calc_value1 = request.form.get('at_calc_value1', '')
            bl_calc_value1 = request.form.get('bl_calc_value1', '')

            weather = request.form.get('weather', '')
            field = request.form.get('field', '')
            lv_at = int(request.form.get('lv_at', session.get('lv_at', 0)) or 0)
            lv_bl = int(request.form.get('lv_bl', session.get('lv_bl', 0)) or 0)

            print(at_power, at_indv, at_eff, lv_at, lv_bl, char_At)
            print(base_hp, bl_power, bl_indv, bl_eff, lv_at, lv_bl,  char_Bl)
            print(types, type1, type2, type3, type4)
            print(at_terastal, bl_terastal)
            print(at_teras_type, bl_teras_type)

            ## 性格 # DBへのパス（Flaskアプリからの相対パス）
            db_path = os.path.join('database', 'nature.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if char_At:
                cursor.execute('SELECT * FROM nature WHERE name = ?', (char_At,))
                row = cursor.fetchone()
                if row and row[1] is not None:
                    at_nature = row[1]
                if row and row[3] is not None:
                    co_nature = row[3]

            if char_Bl:
                cursor.execute('SELECT * FROM nature WHERE name = ?', (char_Bl,))
                row = cursor.fetchone()
                if row and row[2] is not None:
                    bl_nature = row[2]
                if row and row[4] is not None:
                    de_nature = row[4]
            conn.close()

            print(at_nature, co_nature, bl_nature, de_nature)

            ## 実数値
            if not_max:            
                hp_real = int(request.form.get('hp_real', session.get('hp_real', 1)) or 1)
            else:
                hp_real = math.floor(math.floor(base_hp * 2 + hp_indv + hp_eff / 4) * lv_bl / 100) + lv_bl + 10
            at_real = math.floor(math.floor(at_power * 2 + at_indv + at_eff / 4) * lv_bl / 100 + 5) * at_nature
            co_real = math.floor(math.floor(co_power * 2 + co_indv + co_eff / 4) * lv_bl / 100 + 5) * co_nature
            bl_real = math.floor(math.floor(bl_power * 2 + bl_indv + bl_eff / 4) * lv_bl / 100 + 5) * bl_nature
            de_real = math.floor(math.floor(de_power * 2 + de_indv + de_eff / 4) * lv_bl / 100 + 5) * de_nature
            print(hp_real, at_real, co_real, bl_real, de_real)
            
            # もちもの
            if at_calc_value1 != None:
                if at_calc_value1 == 'ブーストエナジー':
                    if property1 == 'こだいかっせい' or 'クォークチャージ' or \
                        property2 == 'こだいかっせい' or 'クォークチャージ' or \
                        property3 == 'こだいかっせい' or 'クォークチャージ':
                        values = {'at_real': at_real, 'co_real': co_real, 'bl_real': bl_real, 'de_real': de_real}

                        # 最大値をもつキー（変数名）を探す
                        choise = max(values, key=values.get)
                    print(choise)

            ## 威力
            intermediate = math.floor(lv_at * 2 / 5 + 2)
            print(intermediate)
            print(power)
            # print("フィールドなどをpowerに掛ける") # 最終威力power_rev
            
            if field == 'エレキフィールド':
                if types == 'でんき':
                    print("フィールド補正")
                    hosei_pow = 1.3
            if field == 'グラスフィールド':
                if types == 'くさ':
                    hosei_pow =  1.3
                # if type == 'じしん': # 技名
                #     multiple2 = 0.5
            if field == 'ミストフィールド':
                if types == 'ドラゴン':
                    hosei_pow = 0.5
            if field == 'サイコフィールド':
                if types == 'エスパー':
                    hosei_pow = 1.3
            if field == None:
                hosei_pow = 1.0

            print(f"フィールド補正:{hosei_pow}")

            power_rev = power * hosei_pow
            # print(power_rev)
            power_rev = kirisute(power_rev)
            print(power_rev)

            ## 最終攻撃
            if at_lank != 0:
                print("Aランク補正")
                if at_lank > 0:
                    at_real = math.floor(at_real * ((abs(at_lank)+2) / 2))
                elif at_lank < 0: 
                    at_real = math.floor(at_real * (2 / (abs(at_lank)+2)))

            if co_lank != 0:
                if co_lank > 0:
                    co_real = math.floor(co_real * ((abs(co_lank)+2) / 2))
                elif co_lank < 0: 
                    co_real = math.floor(co_real * (2 / (abs(co_lank)+2)))

            # print("はりきり") # 四捨五入
            print("攻撃補正") # kirisute()
            
            # もちもの
            if at_calc_value1 != None:
                if at_calc_value1 == 'こだわりハチマキ':
                    hosei_at *= 1.5
                if at_calc_value1 == 'こだわりメガネ':
                    hosei_co *= 1.5

            if choise == 'at_real': # エナジー補正
                hosei_at *= 1.3
            if choise == 'co_real':
                hosei_co *= 1.3
                print(f"エナジー補正:{hosei_co}")

            last_at = at_real * hosei_at
            last_at = kirisute(last_at)
            # print(co_real)
            last_co = co_real * hosei_co
            last_co = kirisute(last_co)
            # print(last_co)

            ## 最終防御
            if weather == 'すな':
                if type3 == 'いわ' or type4 == 'いわ' or bl_teras_type == 'いわ':
                    de_real = math.floor(de_real * 1.5)

            if weather == 'ゆき':
                if type3 == 'こおり' or type4 == 'こおり' or bl_teras_type == 'こおり':
                    bl_real = math.floor(bl_real * 1.5)

            # print(hp_real, at_real, co_real, bl_real, de_real)
            # print(power_rev)

            if bl_lank != 0:
                if bl_lank > 0:
                    bl_real = math.floor(bl_real * ((abs(bl_lank)+2) / 2))
                elif bl_lank < 0: 
                    bl_real = math.floor(bl_real * (2 / (abs(bl_lank)+2)))

            if de_lank != 0:
                if de_lank > 0:
                    de_real = math.floor(de_real * ((abs(de_lank)+2) / 2))
                elif de_lank < 0: 
                    de_real = math.floor(de_real * (2 / (abs(de_lank)+2)))

            # print(hp_real, at_real, co_real, bl_real, de_real)
            # print(power_rev)

            print("防御補正") # kirisute()
            if choise == 'bl_real': # エナジー補正
                hosei_bl *= 1.3
            if choise == 'de_real':
                hosei_de *= 1.3

            last_bl = bl_real * hosei_bl
            last_bl = kirisute(last_bl)
            last_de = de_real * hosei_de
            last_de = kirisute(last_de)


            ## その他補正
            if weather == 'はれ':
                if types == 'ほのお':
                    # print("晴れ補正")
                    multiple2 = 1.5
                if types == 'みず':
                    multiple2 = 0.5
            if weather == 'あめ':
                # print("雨補正")
                if types == 'みず':
                    multiple2 =  1.5
                if types == 'ほのお':
                    multiple2 = 0.5
            if weather == None:
                multiple2 = 1.0

            print(f"天候補正:{multiple2}")


            if at_terastal:
                print("攻撃側テラス")
                if types == type1 or types == type2 or types == at_teras_type:
                    if (types == at_teras_type) and (types == type1 or types == type2):
                        if property1 == 'てきおうりょく' or \
                            property2 == 'てきおうりょく' or \
                            property3 == 'てきおうりょく':
                                print('てきおうりょく発動')
                                multiple *= 2.25        
                        else :
                            multiple *= 2.0
                            print('両方一致タイプ一致') #元とテラスどっちも技と一致
                    else:
                        multiple *= 1.5
                        print('テラスタイプ一致')
                else:
                    multiple *= 1.0
                # print(multiple)
                # power_rev =  power * multiple

            else:
                if types == type1 or types == type2:
                    if property1 == 'てきおうりょく' or \
                        property2 == 'てきおうりょく' or \
                        property3 == 'てきおうりょく':
                            print('てきおうりょく発動')
                            multiple *= 2.0
                            
                    else:
                        multiple *= 1.5
                        print('タイプ一致')
                else:
                    multiple *= 1.0

                # print(multiple)
                # power_rev =  power * multiple

            print(f"タイプ一致{multiple}")

            if types and type3:
               db_path = os.path.join('database', 'type_chart.db')
               conn = sqlite3.connect(db_path)
               cursor = conn.cursor()
               print("ここにはいる？")
               try:
                  if type4 != None:
                     cursor.execute(
                     f"SELECT attacker, [{type3}], [{type4}] FROM type_chart")
                     rows = cursor.fetchone()
                     print(rows)

                     if row in rows:
                       attacker, val3, val4 = row
                       print(attacker)
                       if val3 is not None and val4 is not None and float(val3) >= 1.0 and float(val4) >= 1.0:
                          matching_types.append(attacker)
                  else:
                     cursor.execute(
                     f"SELECT attacker, [{type3}] FROM type_chart")
                     rows = cursor.fetchone()

                     if row in rows:
                        attacker, val3 = row
                        if val3 is not None and val3 >= 1.0:
                            matching_types.append(attacker)
               finally:
                 conn.close()

  
            if bl_terastal:
                print("防御側テラス")
                if types and bl_teras_type:
                    # DBへのパス（Flaskアプリからの相対パス）
                    db_path = os.path.join('database', 'type_chart.db')
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT attacker FROM type_chart")
                    print(cursor.fetchall)

                    try:
                        # type vs item_bl.type1
                        cursor.execute(
                            # 'SELECT multiplier FROM type_chart WHERE attacking_type=? AND defending_type=?',
                            # (type, item_bl.type1)
                            f"SELECT [{bl_teras_type}] FROM type_chart WHERE attacker = ?",
                            (types,)
                        )
                        row = cursor.fetchone()
                        if row and row[0] is not None:
                            match1 = row[0]

                        type_multiplier = match1

                        # power_rev = power * type_multiplier
                            

                        print(f"タイプ相性補正: {type_multiplier}")

                    finally:
                        conn.close()
            else:
                if types and type3:
                    # DBへのパス（Flaskアプリからの相対パス）
                    db_path = os.path.join('database', 'type_chart.db')
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    try:
                        # type vs item_bl.type1
                        cursor.execute(
                            # 'SELECT multiplier FROM type_chart WHERE attacking_type=? AND defending_type=?',
                            # (type, item_bl.type1)
                            f"SELECT [{type3}] FROM type_chart WHERE attacker = ?",
                            (types,)
                        )
                        row = cursor.fetchone()
                        if row and row[0] is not None:
                            match1 = row[0]

                        # type vs item_bl.type2
                        if type4 != None:
                            cursor.execute(
                                f"SELECT [{type4}] FROM type_chart WHERE attacker = ?",
                                (types,)
                            )
                            row = cursor.fetchone()
                            if row and row[0] is not None:
                                match2 = row[0]

                            type_multiplier = match1 * match2 
                        else:
                            type_multiplier = match1

                        # power_rev = power * type_multiplier
                            

                        print(f"タイプ相性補正: {type_multiplier}")

                    finally:
                        conn.close()

            if type_multiplier == 0.0:
                type_match = '無効'
                print("無効だよ")
                print(type_match)
            if  1.0 > type_multiplier > 0.0:
                type_match = 'いまひとつ'
            if type_multiplier == 1.0:
                type_match = '等倍'
            if 1.0 < type_multiplier:
                type_match = '抜群'

            ## ダメージの補正値
            if at_calc_value1 != None:
                if at_calc_value1 == 'いのちのたま':
                    print("いのちのたまありけり")
                    hosei_dmg *= 1.3

            if skill_type == 'physical':
                print("基本ダメージ")
                print(intermediate , power_rev, last_at , last_bl)
                total_dmg = math.floor(intermediate * power_rev * last_at / last_bl)
                print("あれ")
                total_dmg = math.floor(total_dmg / 50 + 2)
                # print(total_dmg)
                total_dmg = kirisute_calc(total_dmg, multiple2) # 天候
                # print(total_dmg)
                total_dmg = kirisute_calc(total_dmg, multiple) # タイプ一致
                # print(total_dmg)
                total_dmg = math.floor(total_dmg * type_multiplier) # タイプ相性
                # print(total_dmg)
                total_dmg = kirisute_calc(total_dmg,  hosei_dmg) # ダメージの補正値
                # print(total_dmg)
            
            elif skill_type == 'special':
                print("基本ダメージ")
                print(intermediate , power_rev , co_real , de_real)
                print("ん？")
                total_dmg = math.floor(intermediate * power_rev * last_co / last_de)
                # print(total_dmg)
                total_dmg = math.floor(total_dmg / 50 + 2)
                # print(total_dmg)
                total_dmg = kirisute_calc(total_dmg, multiple2) # 天候
                # print(total_dmg)
                total_dmg = kirisute_calc(total_dmg, multiple) # タイプ一致
                # print(total_dmg)
                total_dmg = math.floor(total_dmg * type_multiplier) # タイプ相性
                # print(total_dmg)
                # print(hosei_dmg)
                total_dmg = kirisute_calc(total_dmg,  hosei_dmg) # ダメージの補正値
                # print(total_dmg)
            else:
                total_dmg = intermediate

            print(total_dmg)
            print("ダメ計終了")

            min_dmg = math.floor(total_dmg * 0.85)
            max_dmg = math.floor(total_dmg * 1.00)

            if bl_dynamax:
                # 例として：レベル1なら1.2倍、レベル2なら1.4倍、レベル3なら1.6倍...
                multiplier = 1.50 + (0.05 * bl_dynamax_level)
                dym_hp_real = math.floor(hp_real * multiplier)
                dym_base_hp = math.floor(base_hp * multiplier)
                print(f"防御側ダイマックス適用: レベル={bl_dynamax_level}, 倍率={multiplier}")

                print(dym_hp_real, at_real, co_real, bl_real, de_real)
                # print(power_rev)
                print(dym_base_hp)

            print(hp_real, at_real, co_real, bl_real, de_real)
            # print(power_rev)
            print(base_hp)

            if bl_dynamax:
                print("防御側ダイマ")
                min_hp = dym_hp_real - min_dmg
                max_hp = dym_hp_real - max_dmg

                par = (dym_hp_real - min_hp) / dym_hp_real

                if par >= 1:
                    kill = 1
                elif 0.5 <= par < 1.0:
                    kill = 2
                elif 0.33 <= par < 0.5:
                    kill = 3
                elif 0.25 <= par < 0.33:
                    kill = 4
                else:
                    kill = 5

                par_min = round(((dym_hp_real - min_hp) / dym_hp_real) * 100 , 1)
                par_max = round(((dym_hp_real - max_hp) / dym_hp_real) * 100 , 1)

            else:
                min_hp = hp_real - min_dmg
                max_hp = hp_real - max_dmg

                par = (hp_real - min_hp) / hp_real

                if par >= 1:
                    kill = 1
                elif 0.5 <= par < 1.0:
                    kill = 2
                elif 0.33 <= par < 0.5:
                    kill = 3
                elif 0.25 <= par < 0.33:
                    kill = 4
                else:
                    kill = 5

                par_min = round(((hp_real - min_hp) / hp_real) * 100 , 1)
                par_max = round(((hp_real - max_hp) / hp_real) * 100 , 1)

    else:
        # GETリクエスト時の初期値設定
        search_name_At = session.get('search_name_At', '')
        search_name_Bl = session.get('search_name_Bl', '')
        power = session.get('power', 1)
        at_power = session.get('at_power', 1)
        co_power = session.get('co_power', 1)
        bl_power = session.get('bl_power', 1)
        de_power = session.get('de_power', 1)
        base_hp = session.get('base_hp', 1)
        hp_real = session.get('hp_real', 1)
        at_lank= session.get('at_lank', 0)
        co_lank = session.get('co_lank', 0)
        bl_lank = session.get('bl_lank', 0)
        de_lank = session.get('de_lank', 0)
        at_dynamax_level = session.get('at_dynamax_level', 0)
        bl_dynamax_level = session.get('bl_dynamax_level', 0)
        at_teras_type = session.get('at_teras_type', '')
        bl_teras_type = session.get('bl_teras_type', '')
        lv_at = session.get('lv_at', 0)
        lv_bl = session.get('lv_bl', 0)
        types = session.get('types', '')


    context = dict(
        lv_at=session.get('lv_at', 0),
        lv_bl = session.get('lv_bl', 0),
        search_name_At=session.get('search_name_At', ''),
        search_name_Bl=session.get('search_name_Bl', ''),
        char_At=char_At,
        char_Bl=char_Bl,
        skill_type=skill_type,
        types=session.get('types', ''),
        
        at_dynamax_level = session.get('at_dynamax_level', ''),
        bl_dynamax_level = session.get('bl_dynamax_level', ''),
        at_teras_type = session.get('at_teras_type', ''),
        bl_teras_type = session.get('bl_teras_type', ''),
        
        power=power,

        at_power=session.get('at_power', ''),
        co_power=session.get('co_power', ''),
        bl_power=session.get('bl_power', ''),
        de_power=session.get('de_power', ''),
        
        hp_eff=hp_eff,
        at_eff=at_eff,
        co_eff=co_eff,
        bl_eff=bl_eff,
        de_eff=de_eff,

        hp_indv=hp_indv,
        at_indv=at_indv,
        co_indv=co_indv,
        bl_indv=bl_indv,
        de_indv=de_indv,

        at_lank=at_lank,
        co_lank=co_lank,
        bl_lank=bl_lank,
        de_lank=de_lank,
        
        at_calc_value1=at_calc_value1,
        bl_calc_value1=bl_calc_value1,
        weather=weather,
        field=field,

        total_dmg=total_dmg,
        min_dmg=min_dmg,
        max_dmg=max_dmg,
        base_hp = session.get('base_hp', 1),
        hp_real=hp_real,
        min_hp=min_hp,
        max_hp=max_hp,
        par=par,
        kill=kill,
        par_min=par_min,
        par_max=par_max,
        type_match=type_match,
        matching_types=matching_types
    )

    # 非同期リクエストの場合は部分テンプレートを返す
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('partials/cobs2_content.html', **context)

    # 通常リクエストは全体テンプレート
    return render_template('cobs2.html', **context)


@app.route('/type_chart')
def show_type_chart():
    conn = sqlite3.connect(type_chart_db_path)
    df = pd.read_sql_query("SELECT * FROM type_chart", conn)
    conn.close()

    context = dict(
        tables=[df.to_html(classes='data')],
        titles=df.columns.values
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('partials/type_chart_content.html', **context)

    return render_template('type_chart.html', **context)


if __name__ == '__main__':
    with app.app_context():
        init_db_from_csv()
    # app.run(host="0.0.0.0", port=80, debug=True)
    app.run(debug=True)
