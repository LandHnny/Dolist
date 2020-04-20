#encoding: utf-8
import os
#redirect重定向，URL_for取得地址,render_template加入index
from flask import Flask,url_for,redirect,render_template,session,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app, use_native_unicode='utf8')
from flaskr.models import User,Task,User_task
db.create_all()

# 返回主页
@app.route('/')
def index():
    un = session.get('username')
    return render_template("index.html",username=un)

# 登录
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        un = request.form.get('name')
        pw = request.form.get('password')
        # 查询
        res = User.query.filter(User.username == un).first()
        if res:
            if pw == res.password:
                session['userid'] = res.id
                session['username'] = un
                session['password'] = pw
                return redirect(url_for('index'))
            else:
                return redirect(url_for('default',bad='falseUser'))
        else:
            return redirect(url_for('default',bad='noUser'))

# 注册
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        un = request.form.get('name')
        pw = request.form.get('password')
        res = User.query.filter(User.username == un).first()
        if res:
            return redirect(url_for('default',bad='haveUser'))
        else:
            user = User(username=un,password=pw)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('default',bad='goodRegister'))

# 新建任务
@app.route('/newTask',methods=['POST','GET'])
def newTask():
    if request.method == 'GET':
        res = User.query.filter().all()
        return render_template("newTask.html",res=res)
    else:
        re = request.form.getlist('receivers')
        dl = request.form.get('deadline')
        hl = request.form.get('headline')
        ct = request.form.get('content')
        now = datetime.now()
        task = Task(headline=hl,content=ct,creation_time=now,deadline=dl)
        db.session.add(task)
        db.session.flush()
        t_id = task.id
        db.session.commit()
        se_id = session.get('userid')
        for re_id in re:
            ut = User_task(task_id=int(t_id),receiver_id=int(re_id),sender_id=int(se_id))
            db.session.add(ut)
            db.session.commit()
        return redirect('/')
        
# 发送任务

# 删除任务

# 修改任务的预完成时间

# 查看待办事项
@app.route('/todolist')
def todolist():
    t = []
    re_id = session.get('userid')
    ut = User_task.query.filter(User_task.receiver_id==re_id).all()
    k = 0
    for r in ut:
        if r.finish_time:
            continue
        else:
            k = k+1
            task = Task.query.filter(Task.id==r.task_id).first()
            i = {}
            i['id'] = k
            i['headline'] = task.headline
            i['content'] = task.content
            i['deadline'] = task.deadline.strftime('%Y-%m-%d')
            i['est'] = r.estimated_time
            t.append(i)
    return render_template("todolist.html",t=t)

# 查看任务反馈
@app.route('/taskFeedback')
def taskFeedback():
    t = []
    se_id = session.get('userid')
    user_task = User_task.query.filter(User_task.sender_id==se_id).all()
    i = 0
    for ut in user_task:
        i = i+1
        task = Task.query.filter(Task.id==ut.task_id).first()
        user = User.query.filter(User.id==ut.receiver_id).first()
        k = {}
        k['id'] = i
        k['headline'] = task.headline
        k['content'] = task.content
        k['deadline'] = task.deadline.strftime('%Y-%m-%d')
        k['est'] = ut.estimated_time
        k['re'] = user.username
        k['ft'] = ut.finish_time
        t.append(k)
    return render_template("taskFeedback.html",t=t)

# 统计图
@app.route('/statistical')
def  statistical():
    return render_template("statistical.html")

# 删除用户

# 注销登录

# 错误页面
@app.route('/default')
def default():
    return render_template("default.html",w=request.args.get('bad'))

# 检测是否登录
@app.before_request
def mybefore_request():
    if request.path == url_for('index') or \
        request.path == url_for('newTask') or \
        request.path == url_for('todolist') or \
        request.path == url_for('statistical') or \
        request.path == url_for('taskFeedback'):
        if session.get('username'):
            pass
        else:
            return redirect(url_for('login'))
        

if __name__ == '__main__':
    
    app.run()

