DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE tesk (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_time datetime,
  deadline datetime,
  headline TEXT,
  content TEXT
);

CREATE TABLE task_user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  receiver_id INTEGER NOT NULL,
  sender_id INTEGER NOT NULL,
  finish_time datetime,
  estimated_time datetime,
  FOREIGN KEY (task_id) REFERENCES tesk (id)
  FOREIGN KEY (receiver_id) REFERENCES user (id)
  FOREIGN KEY (sender_id) REFERENCES user (id)
);