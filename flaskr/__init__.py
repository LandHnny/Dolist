#encoding: utf-8
import os
#redirect重定向，URL_for取得地址,render_template加入index
from flask import Flask,url_for,redirect,render_template,session,request,jsonify
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
        user = User.query.filter(User.username==un).first()
        if user:
            if pw == user.password:
                session['userid'] = user.id
                session['username'] = un
                return redirect(url_for('index'))
            else:
                return redirect(url_for('default',bad='falseUser'))
        else:
            return redirect(url_for('default',bad='noUser'))

# 注册
@app.route('/register',methods=['POST'])
def register():
    un = request.form.get('name')
    pw = request.form.get('password')
    res = User.query.filter(User.username==un).first()
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
    if request.method=='GET':
        users = User.query.filter().all()
        return render_template("newTask.html",users=users)
    else:
        re = request.form.getlist('receivers')
        dl = request.form.get('deadline')
        hl = request.form.get('headline')
        ct = request.form.get('content')
        se_id = session.get('userid')
        now = datetime.now()
        task = Task(headline=hl,content=ct,creation_time=now,deadline=dl,sender_id=int(se_id))
        db.session.add(task)
        db.session.flush()
        t_id = task.id
        db.session.commit()
        for re_id in re:
            ut = User_task(task_id=int(t_id),receiver_id=int(re_id))
            db.session.add(ut)
            db.session.commit()
        return redirect(url_for('index'))

# 删除任务
@app.route('/deleteTask',methods=['POST'])
def deleteTask():
    u_id = session.get("userid")
    t_id = request.form.get('testId')
    task = Task.query.filter(sender_id==uId,id==t_id).first()
    if task:
        results = User_task.query.filter(task_id==t_id).all()
        db.session.delete(results)
        db.session.delete(task)
        db.session.commit()
        return "任务成功删除"
    else:
        return "任务不存在"

# 修改任务的预完成时间
@app.route('/modifyET',methods=['POST','GET'])
def modifyET():
    if request.method == 'GET':
        return render_template("modifyET.html")
    else:
        et = request.form.getlist('estimated_time')
        t_id = request.form.get('testId')
        u_id = session.get('userid')
        user_task = User_task.query.filter(task_id==t_id,receiver_id==u_id).first()
        user_task.estimated_time = et
        db.session.commit()
        return redirect(url_for('index'))

# 查看待办事项
@app.route('/todolist')
def todolist():
    t = []
    u_id = session.get('userid')
    ut = User_task.query.filter(User_task.receiver_id==u_id).all()
    # k = 0
    for r in ut:
        if r.finish_time:
            continue
        else:
            # k = k+1
            task = Task.query.filter(Task.id==r.task_id).first()
            i = {}
            i['id'] = task.id
            i['headline'] = task.headline
            i['content'] = task.content
            i['deadline'] = task.deadline.strftime('%Y-%m-%d')
            i['est'] = r.estimated_time
            t.append(i)
    return render_template("mission.html",t=t)

# 查看任务反馈
@app.route('/taskFeedback')
def taskFeedback():
    t = []
    se_id = session.get('userid')
    user_task = User_task.query.filter(User_task.sender_id==se_id).all()
    # i = 0
    for ut in user_task:
        # i = i+1
        task = Task.query.filter(Task.id==ut.task_id).first()
        user = User.query.filter(User.id==ut.receiver_id).first()
        k = {}
        k['id'] = task.id
        k['headline'] = task.headline
        k['content'] = task.content
        k['deadline'] = task.deadline.strftime('%Y-%m-%d')
        k['est'] = ut.estimated_time.strftime('%Y-%m-%d')
        k['re'] = user.username
        k['ft'] = ut.finish_time
        t.append(k)
    return render_template("taskFeedback.html",t=t)

# 统计图
@app.route('/statistic',methods=['POST','GET'])
def statistic():
    if request.method == 'GET':
        return render_template("statistic.html")
    else:
        # 发送任务人的姓名,每个人给自己发送任务的数量
        users = []
        number = [] 
        res = {
            "users":[],
            "number":[]
        }
        u_id = session.get('userid')
        user_task = User_task.query.filter(User_task.receiver_id==u_id).all()
        for ut in user_task:
            task = Task.query.filter(id==ut.task_id).first()
            user = User.query.filter(id==task.sender_id).first()
            if user.username in users:
                idx = users.index(user.username)
                number[idx] =  number[idx]+1
            else:
                number.append(1)
                users.append(user.username)
        for i in range(len(number)):
            for j in range(len(number)):
                if number[i]>number[j]:
                    temp = number[i]
                    number[i]=number[j]
                    number[j]=temp
                    temp2=users[i]
                    users[i]=users[j]
                    users[j]=temp2
        res["users"]=users
        res["number"]=number  
        return render_template("statistic.html",res=res)

# 注销登录
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 任务完成
@app.route('/finish',methods=['POST'])
def finish():
    u_id = session.get("userid")
    t_id = request.form.getlist('taskid')
    ut = User_task.query.filter(task_id==t_id,receiver_id==u_id).first()
    ut.finish_time = datetime.now()
    db.session.commit()
    return redirect(url_for('todolist'))

# 错误页面
@app.route('/default')
def default():
    return render_template("default.html",w=request.args.get('bad'))

# 检测是否登录
@app.before_request
def mybefore_request():
    if request.path == url_for('index') or \
        request.path == url_for('newTask') or \
        request.path == url_for('deleteTask') or \
        request.path == url_for('modifyET') or \
        request.path == url_for('todolist') or \
        request.path == url_for('taskFeedback') or \
        request.path == url_for('statistical') or \
        request.path == url_for('logout'):
        if session.get('username'):
            pass
        else:
            return redirect(url_for('login'))
        

if __name__ == '__main__':
    
    app.run()

