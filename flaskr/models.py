#encoding: utf-8
from datetime import datetime, date
from . import app,db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    password = db.Column(db.Text,nullable=False)
    username = db.Column(db.Text,nullable=False)

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    sender_id = db.Column(db.Integer,nullable=False)
    headline = db.Column(db.Text,nullable=False)
    content = db.Column(db.Text,nullable=False)
    creation_time = db.Column(db.DateTime,nullable=False)
    deadline = db.Column(db.DateTime,nullable=False)

class User_task(db.Model):
    __tablename__ = 'user_task'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    task_id = db.Column(db.Integer,nullable=False)
    receiver_id = db.Column(db.Integer,nullable=False)
    finish_time = db.Column(db.DateTime,nullable=True)
    estimated_time = db.Column(db.DateTime,nullable=True)


# res = [
#         {
#             id:
#             headline
#             content
#             creation_time
#             deadline
#             receiver:[
#                 {
#                     reid
#                     username
#                     estimated_time
#                     finish_time
#                 }
#             ]
#         }
#     ]