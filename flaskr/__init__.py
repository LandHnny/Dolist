#encoding: utf-8
import os
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
    if un==Config.ADMINISTRATOR:
        return render_template("ad.html",username=un)
    else:
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
                if user.status == 0:
                    return redirect(url_for('default',bad='noPower'))
                session['userid'] = user.id
                session['username'] = un
                return redirect(url_for('index'))
            else:
                return redirect(url_for('default',bad='falseUser'))
        else:
            if un==Config.ADMINISTRATOR and pw==Config.AD_PASSWORD:
                session['userid'] = -1
                session['username'] = un
                return redirect(url_for('index'))
            return redirect(url_for('default',bad='noUser'))

# 注册
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        un = request.form.get('name')
        pw = request.form.get('password')
        res = User.query.filter(User.username==un).first()
        if res or un==Config.ADMINISTRATOR:
            return redirect(url_for('default',bad='haveUser'))
        else:
            user = User(username=un,password=pw,status=1)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('default',bad='goodRegister'))

# 新建任务
@app.route('/newTask',methods=['POST','GET'])
def newTask():
    if request.method=='GET':
        if session.get('userid')==-1:
            return redirect(url_for('default',bad='ad'))
        users = User.query.filter().all()
        return render_template("newTask.html",users=users)
    else:
        if session.get('userid')==-1:
            return redirect(url_for('default',bad='ad'))
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

# 修改任务的预完成时间
@app.route('/modifyET',methods=['POST','GET'])
def modifyET():
    if session.get('userid')==-1:
        return redirect(url_for('default',bad='ad'))
    et = request.form.getlist('estimated_time')
    if et != ['']:
        t_id = request.form.get('testId')
        u_id = session.get('userid')
        user_task = User_task.query.filter(User_task.task_id==int(t_id),User_task.receiver_id==u_id).first()
        user_task.estimated_time = et
        db.session.commit()
        return redirect(url_for('todolist2'))
    else:
        return redirect(url_for('default',bad='noEst'))

# 查看待办事项
@app.route('/todolist2')
def todolist2():
    if session.get('userid')==-1:
        return redirect(url_for('default',bad='ad'))
    t = []
    u_id = session.get('userid')
    ut = User_task.query.filter(User_task.receiver_id==u_id).all()
    for r in ut:
        if r.finish_time:
            continue
        else:
            task = Task.query.filter(Task.id==r.task_id).first()
            if task:
                sender = User.query.filter(User.id==task.sender_id).first()
                i = {}
                i['id'] = task.id
                i['headline'] = task.headline
                content = '<p>'+task.content.replace('\r\n', '</p><p>')+'</p>'
                i['content'] = content
                i['deadline'] = task.deadline.strftime('%Y-%m-%d')
                i['createTime'] = task.creation_time.strftime('%Y-%m-%d')
                i['sender'] = sender.username
                est = r.estimated_time
                if est:
                    i['est'] = est.strftime('%Y-%m-%d')
                else:
                    i['est'] = est
                t.append(i)
            else:
                continue
    return render_template("mission.html",t=t)

# 查看待办事项
@app.route('/todolist1')
def todolist1():
    t = []
    u_id = session.get('userid')
    ut = User_task.query.filter(User_task.receiver_id==u_id).all()
    for r in ut:
        if r.finish_time:
            continue
        else:
            task = Task.query.filter(Task.id==r.task_id).first()
            if task:
                if int(task.deadline.strftime('%Y%m%d'))<=int(datetime.now().strftime('%Y%m%d')):
                    sender = User.query.filter(User.id==task.sender_id).first()
                    i = {}
                    i['id'] = task.id
                    i['headline'] = task.headline
                    i['content'] = task.content
                    i['deadline'] = task.deadline.strftime('%Y-%m-%d')
                    i['createTime'] = task.creation_time.strftime('%Y-%m-%d')
                    i['sender'] = sender.username
                    est = r.estimated_time
                    if est:
                        i['est'] = est.strftime('%Y-%m-%d')
                    else:
                        i['est'] = est
                    t.append(i)
                else: continue
    return render_template("mission.html",t=t)

# 查看任务反馈
@app.route('/taskFeedback')
def taskFeedback():
    res = []
    se_id = session.get('userid')
    if se_id==-1:
        task = Task.query.filter().all()
    else:
        task = Task.query.filter(Task.sender_id==se_id).all()
    for t in task:
        u = {}
        u["id"] = t.id
        u["headline"] = t.headline
        u["content"] = t.content
        u["createTime"] = t.creation_time.strftime('%Y-%m-%d')
        u["deadline"] = t.deadline.strftime('%Y-%m-%d')
        u["receiver"] = []
        user_task = User_task.query.filter(User_task.task_id==t.id).all()
        for ut in user_task:
            user = User.query.filter(User.id==ut.receiver_id).first()
            k = {}
            k['reid'] = user.id
            k['username'] = user.username
            est = ut.estimated_time
            if est:
                k['est'] = est.strftime('%Y-%m-%d')
            else:
                k['est'] = est
            ft = ut.finish_time
            if ft:
                k['finishTime'] = ft.strftime('%Y-%m-%d')
            else:
                k['finishTime'] = ft
            u["receiver"].append(k)
        res.append(u)
    return render_template("taskFeedback.html",t=res)

@app.route('/statistic')
def statistic():
    return render_template("statistic.html")

# 统计图
@app.route('/echarts',methods=['POST'])
def echarts():
    # 发送任务人的姓名,每个人给自己发送任务的数量
    users = []
    number = [] 
    res = []
    u_id = session.get('userid')
    if u_id==-1:
        user_task = User_task.query.filter().all()
    else:
        user_task = User_task.query.filter(User_task.receiver_id==u_id).all()
    for ut in user_task:
        task = Task.query.filter(Task.id==ut.task_id).first()
        user = User.query.filter(User.id==task.sender_id).first()
        if user.username in users:
            idx = users.index(user.username)
            number[idx] =  number[idx]+1
        else:
            number.append(1)
            users.append(user.username)
    for i in range(0,len(number)):
        for j in range(0,len(number)):
            if number[i]>number[j]:
                temp = number[i]
                number[i]=number[j]
                number[j]=temp
                temp2=users[i]
                users[i]=users[j]
                users[j]=temp2
    for i in range(0,len(users)):
        r={
            "name":users[i],
            "num":number[i]
        }
        res.append(r)
    datas = {}
    datas['data'] = res
    print(datas)
    print(jsonify(datas))
    return jsonify(datas)

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
    ut = User_task.query.filter(User_task.task_id==t_id,User_task.receiver_id==u_id).first()
    ut.finish_time = datetime.now()
    db.session.commit()
    return redirect(url_for('todolist2'))

# 删除任务
@app.route('/deleteTask',methods=['POST'])
def deleteTask():
    t_id = request.form.get('testId')
    u_id = session.get('userid')
    if u_id == -1:
        task = Task.query.filter(Task.id==t_id).first()
    else:
        task = Task.query.filter(Task.id==t_id,Task.sender_id==u_id).first()
    if task:
        user_task = User_task.query.filter(User_task.task_id==t_id).all()
        if user_task:
            for ut in user_task:
                db.session.delete(ut)
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('taskFeedback'))

# 管理用户
@app.route('/users')
def users():
    u_id = session.get('userid')
    if u_id==-1:
        user = User.query.filter().all()
        t=[]
        for i in user:
            k={}
            k['id']=i.id
            k['username']=i.username
            k['password']=i.password
            k['status']=i.status
            t.append(k)
        return render_template("users.html",t=t)
    else:
        return redirect(url_for('default',bad='noPower'))

# 删除用户
@app.route('/deleteUser',methods=['POST'])
def deleteUser():
    id = request.form.get('id')
    u_id = session.get('userid')
    if u_id==-1:
        user = User.query.filter(User.id==id).first()
        task = Task.query.filter(Task.sender_id==id).all()
        for t in task:
            user_task = User_task.query.filter(User_task.task_id==t.id).all()
            for ut in user_task:
                db.session.delete(ut)
            db.session.delete(t)
        user_task = User_task.query.filter(User_task.receiver_id==id).all()
        for ut in user_task:
            db.session.delete(ut)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('users'))
    else:
        return redirect(url_for('default',bad='noPower'))

# 禁用用户
@app.route('/modifyUStatus',methods=['POST'])
def modifyUStatus():
    id = request.form.get('id')
    u_id = session.get('userid')
    if u_id==-1:
        user = User.query.filter(User.id==id).first()
        if user.status==0:
            user.status=1
        else:  
            user.status=0
        db.session.commit()
        return redirect(url_for('users'))
    else:
        return redirect(url_for('default',bad='noPower'))

# 错误页面
@app.route('/default')
def default():
    return render_template("default.html",w=request.args.get('bad'))

# 检测是否登录
@app.before_request
def mybefore_request():
    if request.path == url_for('index') or \
        request.path == url_for('newTask') or \
        request.path == url_for('modifyET') or \
        request.path == url_for('todolist1') or \
        request.path == url_for('todolist2') or \
        request.path == url_for('taskFeedback') or \
        request.path == url_for('statistic') or \
        request.path == url_for('logout'):
        if session.get('username'):
            pass
        else:
            return redirect(url_for('login'))
        

if __name__ == '__main__':
    
    app.run()

