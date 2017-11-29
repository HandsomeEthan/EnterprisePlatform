from flask import Flask,render_template,redirect,url_for,request,session,g
from models import Plate,Theme,Answer,User
import config
from exts import db
from decorators import login_required
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():#首页，板块界面
    # if session.get('plate_id'):
    #     del session['plate_id']
    # cont = {
    #     'bankuais': Plate.query.order_by('-create_time').all()
    # }
    return render_template('index_2.html')

@app.route('/login/',methods=['GET','POST'])
def login():#登录界面
    if request.method=='GET':
        return render_template('login.html')
    else:
        if 'lastpage' in session:
            lastpage=session['lastpage']
            the_id=session['the_id']
            session.pop('lastpage')
            session.pop('the_id')
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session.permanent = True
            if lastpage:
                if lastpage=='theme':
                    return redirect(url_for(lastpage,plate_id=the_id))
                elif lastpage=='detail':
                    return redirect(url_for(lastpage,theme_id=the_id))
            else:
                return redirect(url_for('index'))
        else:
            return '密码错误'

@app.route('/regist/', methods=['GET', 'POST'])
def regist():  # 注册界面
    if request.method=='GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        usersex = request.form.get('sex')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user=User.query.filter(User.telephone==telephone).first()
        if user:
            return '此号码已经被注册过，请更换'
        else:
            if password1!=password2:
                return '两次密码不相同，请重新输入'
            else:
                user=User(telephone=telephone,username=username,usersex=usersex,password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))

@app.route('/theme/<plate_id>/')
def theme(plate_id):#主题界面（点击首页某板块进入此页面）
    session['lastpage'] = 'theme'
    session['the_id'] = plate_id
    session['plate_id'] = plate_id
    session.permanent = True
    contexts = {
        'themes': Theme.query.filter(Theme.plate_id == plate_id).order_by('-create_time').all(),
        'plate_id':plate_id
    }
    return render_template('theme.html',**contexts)

# @app.route('/addBanKuai/',methods=['GET','POST'])
# @login_required
# def addBanKuai():
#     if request.method=='GET':
#         return render_template('addBanKuai.html')
#     else:
#         title=request.form.get('title')
#         plate=Plate(title=title)
#         plate.author=g.user
#         db.session.add(plate)
#         db.session.commit()
#         return redirect(url_for('index'))

@app.route('/put_theme/<plateid>',methods=['GET','POST'])
@login_required
def put_theme(plateid):#向主题界面发布问答主题
    if request.method=='GET':
        return render_template('question.html')
    else:
        title=request.form.get('title')
        content = request.form.get('content')
        plate_id=plateid
        # plate_id=request.form.get('plate_id')
        theme=Theme(title=title,content=content)
        theme.author = g.user
        plate=Plate.query.filter(Plate.id==plate_id).first()
        theme.plate=plate
        m=0
        for x in Theme.query.all():  # 迭代器，
            if x.plate_id == theme.plate_id:
                m = m + 1
        plate.post_num = m
        db.session.add(theme)
        db.session.commit()
        return redirect(url_for('theme',plate_id=plate.id))

@app.route('/detail/<theme_id>/')
def detail(theme_id):#详情界面（点击主题界面某主题进入此页面）
    session['lastpage'] = 'detail'
    session['the_id'] = theme_id
    theme_model=Theme.query.filter(Theme.id==theme_id).first()
    return render_template('detail.html',theme=theme_model)

@app.route('/add_answer/',methods=['POST'])
@login_required
def add_answer():#对主题详情进行评论
    content = request.form.get('answer_content')
    theme_id = request.form.get('theme_id')
    answer=Answer(content=content)
    answer.author = g.user
    answer.father_answer_id=0
    theme = Theme.query.filter(Theme.id == theme_id).first()
    answer.plate_id=theme.plate_id
    answer.theme = theme
    m = 0
    for x in Answer.query.all():  # 迭代器，遍历Answer数据表中的每一个数据
        if x.theme_id == answer.theme_id:
            m = m + 1
    theme.answer_num = m
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',theme_id=theme.id))

@app.route('/huifu/<father_answer_id>',methods=['GET','POST'])
@login_required
def huifu(father_answer_id):
    if request.method=='GET':
        return render_template('huifu.html')
    else:
        father_answer_id = father_answer_id
        answer = Answer.query.filter(Answer.id == father_answer_id).first()
        content = request.form.get('huifu_content')
        huifu = Answer(content=content)
        huifu.father_answer_id = father_answer_id
        theme = Theme.query.filter(Theme.id == answer.theme_id).first()
        huifu.theme = theme
        huifu.plate_id = answer.plate_id
        huifu.author = g.user
        db.session.add(huifu)
        db.session.commit()
        return redirect(url_for('detail', theme_id=theme.id))

# @app.route('/search/')
# def search():#在主题页根据关键字搜索对应主题
#     q = request.args.get('q')
#     condition = or_(Theme.title.contains(q), Theme.content.contains(q))
#     themes = Theme.query.filter(condition).order_by('-create_time')
#     return render_template('theme.html', themes)

@app.route('/logout/')
def logout():#注销
    session.clear()
    return redirect(url_for('login'))

@app.before_request
def my_before_request():
    user_id=session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user=user

@app.before_request
def my_before_request():
    plate_id=session.get('plate_id')
    if plate_id:
        plate = Plate.query.filter(Plate.id == plate_id).first()
        if plate:
            g.plate=plate

@app.context_processor
def my_context_proceeor():
    if hasattr(g,'user'):
        return {'user':g.user}
    else:
        return {}

@app.context_processor
def my_context_proceeor():
    if hasattr(g,'plate'):
        return {'plate':g.plate}
    else:
        return {}

if __name__ == '__main__':
    app.run()
