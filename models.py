from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash


class Plate(db.Model):
    __tablename__='plate'
    id=db.Column(db.INTEGER,primary_key=True,autoincrement=True)#板块编号
    title=db.Column(db.String(100),nullable=False)#板块名称
    #author_id=db.Column(db.INTEGER,db.ForeignKey('user.id'))#版主编号
    post_num=db.Column(db.INTEGER,default=0)#帖子数目
    #father_id=db.Column(db.INTEGER,nullable=False)#父板块编号
    create_time = db.Column(db.DateTime, default=datetime.now)

    #author=db.relationship('User',backref=db.backref('plate'))


class Theme(db.Model):
    __tablename__='theme'
    id=db.Column(db.INTEGER,primary_key=True,autoincrement=True)#帖子编号
    title=db.Column(db.String(100), nullable=False)#帖子标题
    content=db.Column(db.Text, nullable=False)#帖子内容
    answer_num=db.Column(db.INTEGER, default=0)#回复的评论数目
    create_time = db.Column(db.DateTime, default=datetime.now)  # 发帖时间

    plate_id=db.Column(db.INTEGER,db.ForeignKey('plate.id'))#所属板块编号
    author_id=db.Column(db.INTEGER,db.ForeignKey('user.id'))#发帖用户编号

    plate=db.relationship('Plate',backref=db.backref('themes'))#帖子与板块建立连接（通过帖子访问所属板块，通过板块得到其中的帖子）
    author=db.relationship('User',backref=db.backref('themes'))#帖子与发帖人建立连接


class Answer(db.Model):
    __tablename__='answer'
    id=db.Column(db.INTEGER,primary_key=True,autoincrement=True)#评论编号
    create_time=db.Column(db.DateTime,default=datetime.now)#发表评论的时间
    content = db.Column(db.Text, nullable=False)

    father_answer_id = db.Column(db.INTEGER, default=0)#此评论是哪一篇评论的回复
    theme_id=db.Column(db.INTEGER,db.ForeignKey('theme.id'))#被回复的主帖编号
    plate_id=db.Column(db.INTEGER,db.ForeignKey('plate.id'))#评论所在版块编号
    author_id=db.Column(db.INTEGER,db.ForeignKey('user.id'))#评论人编号

    theme=db.relationship('Theme',backref=db.backref('answers',order_by=id.desc()))#评论与帖子建立连接
    author=db.relationship('User',backref=db.backref('answers'))#评论与评论作者建立连接


class User(db.Model):
    __tablename__='user'
    id=db.Column(db.INTEGER,primary_key=True,autoincrement=True)#用户编号
    username=db.Column(db.String(50),nullable=False)#用户名
    telephone=db.Column(db.String(11),nullable=False)#手机号
    password=db.Column(db.String(100),nullable=False)#密码
    usersex=db.Column(db.String(11),nullable=False)#性别

    def __init__(self, *args, **kwargs):
        telephone = kwargs.get('telephone')
        username = kwargs.get('username')
        password = kwargs.get('password')
        usersex = kwargs.get('usersex')

        self.telephone = telephone
        self.username = username
        self.usersex=usersex
        self.password = generate_password_hash(password)

    def check_password(self, raw_password):
        result = check_password_hash(self.password, raw_password)
        return result