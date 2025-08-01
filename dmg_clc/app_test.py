from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import sqlite3
import math

app = Flask(__name__)
app.secret_key = 'secret'  # 必須

# BASE_DIR を使って database フォルダの中の DB にパスを指定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(BASE_DIR, 'database')
os.makedirs(db_dir, exist_ok=True)  # フォルダがない場合は作成

db_path = os.path.join(db_dir, 'data.db')
type_chart_db_path = os.path.join(db_dir, 'type_chart.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# モデル定義
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    type1 = db.Column(db.String(50))
    type2 = db.Column(db.String(50))
    property1 = db.Column(db.String(50))
    property2 = db.Column(db.String(50))
    property3 = db.Column(db.String(50))
    property4 = db.Column(db.String(50))

    hp = db.Column(db.Integer)  # 'value' ではなく CSV に合わせて 'HP'
    at = db.Column(db.Integer)  
    bl = db.Column(db.Integer)  
    co = db.Column(db.Integer)  
    de = db.Column(db.Integer)  
    sp = db.Column(db.Integer)  

# 初期化関数
def init_db_from_csv():
    if not os.path.exists(db_path):
        db.create_all()
        csv_path = os.path.join(BASE_DIR, 'data', 'data.csv')
        df = pd.read_csv(csv_path)

        # id欠損を削除しint化
        df = df.dropna(subset=['Hp'])
        df['id'] = df['id'].astype(int)
        df['Hp'] = df['Hp'].astype(int)
        df['At'] = df['At'].astype(int)
        df['Bl'] = df['Bl'].astype(int)
        df['Co'] = df['Co'].astype(int)
        df['De'] = df['De'].astype(int)
        df['Sp'] = df['Sp'].astype(int)


        for _, row in df.iterrows():
            item = Item(id=row['id'], name=row['name'], type1=row['type1'], type2=row['type2'], 
                        property1=row['property1'], property2=row['property2'], property3=row['property3'], property4=row['property4'],
                        hp=row['Hp'], at=row['At'], bl=row['Bl'], co=row['Co'], de=row['De'], sp=row['Sp'])
            db.session.add(item)
        db.session.commit()
        print("DB initialized from CSV")

# @app.route('/')
# def index():
#     search_name = request.args.get('search_name', default='', type=str).strip()

#     if search_name:
#         # nameがsearch_nameを含むレコードを検索（部分一致）
#         items = Item.query.filter(Item.name.like(f'%{search_name}%')).all()
#     else:
#         items = Item.query.all()

#     return render_template('cobs2.html', data=items, search_name=search_name)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     # init
#     search_name_At = ''
#     search_name_Bl = ''
#     base_hp = None # HP値(実数)
    
#     lv = 50 # レベル
#     char_At = None # 攻撃側性格
#     char_Bl = None # 防御側性格

#     skill_type = None # 技タイプ(物理/特殊)
#     power = None # 技の威力
#     at_power = None # 攻撃力(物理)
#     co_power = None # 攻撃力(特殊)

#     bl_power = None # 防御力(物理)
#     de_power = None # 防御力(特殊)

#     # 実数値
#     at_real = None
#     co_real = None
#     bl_real = None
#     de_real = None

#     # 努力値
#     at_eff = None
#     co_eff = None
#     bl_eff = None
#     de_eff = None

#     # 個体値
#     at_indv = None
#     co_indv = None
#     bl_indv = None
#     de_indv = None
    
#     calc_value = None # 追加要素
#     total_dmg = None # 合計ダメージ
    
#     min_dmg = None # 最小ダメージ
#     max_dmg = None # 最大ダメージ
    

#     if request.method == 'POST':
#         action = request.form.get('action')

#         if action == 'search':
#             search_name_At = request.form.get('search_name_At', '').strip()
#             search_name_Bl = request.form.get('search_name_Bl', '').strip()
#             if search_name_At:
#                 item = Item.query.filter(Item.name.like(f'%{search_name_At}%')).first()
#                 if item:
#                     at_power = item.at
#                     co_power = item.co
#             if search_name_Bl:
#                 item = Item.query.filter(Item.name.like(f'%{search_name_Bl}%')).first()
#                 if item:
#                     bl_power = item.bl
#                     de_power = item.de

#         elif action == 'calculate':
#             try:
                
#                 skill_type = request.form.get('skill_type')
#                 power = int(request.form.get('power', 0))
#                 # base_hp = int(request.form.get('base_hp', 0))
#                 char_At = float(request.form.get('char_At',1))
#                 char_Bl= float(request.form.get('char_Bl', 1))

#                 at_power = int(request.form.get('at_power', 1))
#                 co_power = int(request.form.get('co_power', 1))
#                 bl_power = int(request.form.get('bl_power', 1))
#                 de_power = int(request.form.get('de_power', 1))

#                 at_indv = int(request.form.get('at_indv', '0'))
#                 co_indv = int(request.form.get('co_indv', '0'))
#                 bl_indv = int(request.form.get('bl_indv', '0'))
#                 de_indv = int(request.form.get('de_indv', '0'))

#                 at_eff= int(request.form.get('at_eff','0'))
#                 co_eff= int(request.form.get('co_eff','0'))
#                 bl_eff= int(request.form.get('bl_eff','0'))
#                 de_eff= int(request.form.get('de_eff','0'))

#                 calc_value = int(request.form.get('calc_value', 0))

#                 print(at_power, at_indv, at_eff, lv, char_At)

#                 at_power = ((at_power * 2 + at_indv + at_eff / 4) * lv / 100 + 5) * char_At
#                 co_power = ((co_power * 2 + co_indv + co_eff / 4) * lv / 100 + 5) * char_At
#                 bl_power = ((bl_power * 2 + bl_indv + bl_eff / 4) * lv / 100 + 5) * char_Bl
#                 de_power = ((de_power * 2 + de_indv + de_eff / 4) * lv / 100 + 5) * char_Bl
                
#                 intermediate = math.floor(lv * 2 / 5 + 2 )
#                 if skill_type == 'physical': # 物理
#                     total_dmg = math.floor(intermediate * at_power / bl_power)
#                     total_dmg = math.floor(total_dmg / 50 + 2)
#                 elif skill_type == 'special': # 特殊
#                     total_dmg = math.floor(intermediate * co_power / de_power)
#                     total_dmg = math.floor(total_dmg / 50 + 2)
#                 else:
#                     total_dmg = intermediate

#                 min_dmg = math.floor(total_dmg * 0.85)
#                 max_dmg = math.floor(total_dmg * 1.00)
#             except ValueError:
#                 pass

#     return render_template(
#         'cobs2.html',
#         lv=lv,
#         search_name_At=search_name_At,
#         search_name_Bl=search_name_Bl,
#         char_At=char_At,
#         char_Bl=char_Bl,

#         # base_hp=base_hp,
#         skill_type=skill_type,
#         power=power,

#         at_power= at_power,
#         co_power=co_power,
#         bl_power=bl_power,
#         de_power=de_power,
        
#         at_eff=at_eff,
#         co_eff=co_eff,
#         bl_eff=bl_eff,
#         de_eff=de_eff,

#         at_indv=at_indv,
#         co_indv=co_indv,
#         bl_indv=bl_indv,
#         de_indv=de_indv,
        
#         calc_value=calc_value,
#         total_dmg=total_dmg,
#         min_dmg=min_dmg,
#         max_dmg=max_dmg
#     )

@app.route('/', methods=['GET', 'POST'])
def index():
    search_name_At = ''
    search_name_Bl = ''
    lv = 50  # レベル

    # 初期値を設定
    char_At = 1.0
    char_Bl = 1.0
    skill_type = None
    power = 0
    calc_value = 0

    # 能力値なども初期値
    at_power = co_power = bl_power = de_power = 1
    at_indv = co_indv = bl_indv = de_indv = 0
    at_eff = co_eff = bl_eff = de_eff = 0
    at_real = co_real = bl_real = de_real = 1

    total_dmg = min_dmg = max_dmg = None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'search_at':
            search_name_At = request.form.get('search_name_At', '').strip()
            session['search_name_At'] = search_name_At  # セッションに保存
            
            if search_name_At:
                item = Item.query.filter(Item.name.like(f'%{search_name_At}%')).first()
                if item:
                    at_power = item.at or 1
                    co_power = item.co or 1
                    session['at_power'] = at_power
                    session['co_power'] = co_power

        elif action == 'search_bl':
            search_name_Bl = request.form.get('search_name_Bl', '').strip()
            session['search_name_Bl'] = search_name_Bl  # セッションに保存
            if search_name_Bl:
                item = Item.query.filter(Item.name.like(f'%{search_name_Bl}%')).first()
                if item:
                    bl_power = item.bl or 1
                    de_power = item.de or 1
                    session['bl_power'] = bl_power
                    session['de_power'] = de_power

        elif action == 'calculate':
            skill_type = request.form.get('skill_type')
            power = int(request.form.get('power', 0) or 0)
            char_At = float(request.form.get('char_At', 1) or 1)
            char_Bl = float(request.form.get('char_Bl', 1) or 1)

            at_power = int(request.form.get('at_power', 1) or 1)
            co_power = int(request.form.get('co_power', 1) or 1)
            bl_power = int(request.form.get('bl_power', 1) or 1)
            de_power = int(request.form.get('de_power', 1) or 1)

            at_indv = int(request.form.get('at_indv', 0) or 0)
            co_indv = int(request.form.get('co_indv', 0) or 0)
            bl_indv = int(request.form.get('bl_indv', 0) or 0)
            de_indv = int(request.form.get('de_indv', 0) or 0)

            at_eff = int(request.form.get('at_eff', 0) or 0)
            co_eff = int(request.form.get('co_eff', 0) or 0)
            bl_eff = int(request.form.get('bl_eff', 0) or 0)
            de_eff = int(request.form.get('de_eff', 0) or 0)

            calc_value = int(request.form.get('calc_value', 0) or 0)

            print(at_power, at_indv, at_eff, lv, char_At)
            print(bl_power, bl_indv, bl_eff, lv, char_Bl)

            # 計算
            at_real = ((at_power * 2 + at_indv + at_eff / 4) * lv / 100 + 5) * char_At
            co_real = ((co_power * 2 + co_indv + co_eff / 4) * lv / 100 + 5) * char_At
            bl_real = ((bl_power * 2 + bl_indv + bl_eff / 4) * lv / 100 + 5) * char_Bl
            de_real = ((de_power * 2 + de_indv + de_eff / 4) * lv / 100 + 5) * char_Bl

            print(at_real, co_real, bl_real, de_real, power)

            intermediate = math.floor(lv * 2 / 5 + 2)
            print(intermediate)

            if skill_type == 'physical':
                total_dmg = math.floor(intermediate * power * at_real / bl_real)
                print("あれ")
                print(total_dmg)
                total_dmg = math.floor(total_dmg / 50 + 2)
            elif skill_type == 'special':
                print(total_dmg)
                total_dmg = math.floor(intermediate * power * co_real / de_real)
                total_dmg = math.floor(total_dmg / 50 + 2)
            else:
                total_dmg = intermediate

            print(total_dmg)

            min_dmg = math.floor(total_dmg * 0.85)
            max_dmg = math.floor(total_dmg * 1.00)

    return render_template(
        'cobs2.html',
        lv=lv,
        search_name_At=session.get('search_name_At', ''),
        search_name_Bl=session.get('search_name_Bl', ''),
        char_At=char_At,
        char_Bl=char_Bl,
        skill_type=skill_type,
        power=power,
        at_power=session.get('at_power', ''),
        co_power=session.get('co_power', ''),
        bl_power=session.get('bl_power', ''),
        de_power=session.get('de_power', ''),
        at_eff=at_eff,
        co_eff=co_eff,
        bl_eff=bl_eff,
        de_eff=de_eff,
        at_indv=at_indv,
        co_indv=co_indv,
        bl_indv=bl_indv,
        de_indv=de_indv,
        calc_value=calc_value,
        total_dmg=total_dmg,
        min_dmg=min_dmg,
        max_dmg=max_dmg
    )


@app.route('/type_chart')
def show_type_chart():
    conn = sqlite3.connect(type_chart_db_path)
    df = pd.read_sql_query("SELECT * FROM type_chart", conn)
    conn.close()
    return render_template('type_chart.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

if __name__ == '__main__':
    with app.app_context():
        init_db_from_csv()
    app.run(debug=True)
