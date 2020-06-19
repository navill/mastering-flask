# Flask TIL - Chapter.2

### SQLAlchemy 설정

```python
pip install flask-sqlalchemy  # sqlite
pip install pymysql

export FLASK_APP=main.py
flask shell
>> db.create_all()  # db migrate
```



### Driver setting

```python
# uri syntax
# databasetype+driver://user:password@host:port/db_name 
# SQLite
sqlite:///database.db 
# MySQL 
mysql+pymysql://user:password@ip:port/db_name 
# Postgres 
postgresql+psycopg2://user:password@ip:port/db_name 
# MSSQL 
mssql+pyodbc://user:password@dsn_name 
# Oracle 
oracle+cx_oracle://user:password@ip:port/db_name
```

**config.py**

```python
# common setting
class Config(object): 
    	pass 

# product level
class ProdConfig(Config): 
		  pass 	

# development level
class DevConfig(Config): 
      debug = True 
      SQLALCHEMY_DATABASE_URI = "sqlite:///database.db" 
      SQLALCHEMY_ECHO = True  # SQL 쿼리문으로 변환하여 로그에 출력
```

**main.py**

```python
from flask import Flask 
from config import DevConfig 
 
app = Flask(__name__) 
app.config.from_object(DevConfig) 
 
@app.route('/') 
def home(): 
    return '<h1>Hello World!</h1>' 
 
if __name__ == '__main__': 
    app.run() 
```

**Flask 실행**

```python
$ export FLASK_APP=main.py
$ flask run
$ flask shell  # django shell과 유사
>>> app.url_map  # 구성된 url map 출력
# '/'과 '/static/filename'으로 구성됨
Map([<Rule '/' (OPTIONS, GET, HEAD) -> home>,  
 <Rule '/static/<filename>' (OPTIONS, GET, HEAD) -> static>])
>>> app.static_folder  # static folder
/chapter_1/static'
>>> app.template_folder  # template folder
'templates'


```



### Modeling

```python
class User(db.Model): 
	  __tablename__ = 'user_table' 
  	id = db.Column(db.Integer(), primary_key=True) 
    username = db.Column(db.String(255)) 
    # username = db.Column('user_name', db.String(255))
    password = db.Column(db.String(255)) 
```

- 필드 이름을 지정할 경우 db.Column('column_name', ...)



**User table 생성(manage.py)**

```python
from main import app, db, User 

@app.shell_context_processor
def make_shell_context():
	  return dict(app=app, db=db, User=User) 
  
# Tell Flask where to load our shell context
$ export FLASK_APP=manage.py
$ flask shell
>>> db.create_all()
# User 테이블이 포함된 database.db 생성됨

# 테이블 확인
$ sqlite3 database.db .tables
user
```



### CRUD

- DB에 새로운 행을 추가할 때: session에 추가 -> commit model object

  ```python
  # pagination
  User.query.paginate(1, 10)
  
  # ascending
  >>> users = User.query.order_by(User.username).all()
  # descending
  >>> users = User.query.order_by(User.username.desc()).all()
  
  # filtering
  >>> users = User.query.filter_by(username='fake_name').all()  # 정확한 값을 알고 있을 때 
  >>> user = User.query.filter(User.id > 1).all()  # python 비교구문을 이용해 범위를 지정할 때 
  
  # order + filter
  >>> users = User.query.order_by(User.username.desc()).filter_by(username='fake_name').limit(2).all()
  
  
  
  # NOT, OR, IN
  >>> from sqlalchemy.sql.expression import not_, or_
  >>> user = User.query.filter(    User.username.in_(['fake_name']),User.password == None).first()
  # password를 가지고 있는 모든 유저
  >>> user = User.query.filter(not_(User.password == None)).first()
  # OR + NOT
  >>> user = User.query.filter(or_(not_(User.password == None), User.id >= 1)).first()
  ```

- Get

  ```python
  >>> user = User(username='fake_name')
  >>> db.session.add(user)
  >>> db.session.commit()
  
  # query.all
  >>> users = User.query.all()
  >>> users
  [<User 'fake_name'>]
  
  
  # query.get
  >>> user = User.query.get(1)
  >>> user.username
  fake_name
  ```

- Update

  ```python
  >>> User.query.filter_by(username='fake_name').update({    'password': 'test'})
  # 업데이트 될 모델은 이미 session에 올라와있는 상태
  >>> db.session.commit()
  ```

- Delete

  ```python
  >>> user = User.query.filter_by(username='fake_name').first()
  >>> db.session.delete(user)
  >>> db.session.commit()
  ```

  

### Relationships between models

- SQLite 및 MySQL/MyISAM에서는 제약사항을 강제하지 않음

  - 필요할 경우 외래키 제약사항을 입력할 코드구문을 작성해야한다.

    ```python
    # constraint of foreign key
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    ```

    

**One-to-many**

```python
class Post(db.Model): 
    id = db.Column(db.Integer(), primary_key=True) 
    title = db.Column(db.String(255)) 
    text = db.Column(db.Text()) 
    publish_date = db.Column(db.DateTime()) 
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id')) 
```

- user_id: Post 모델이 참조할 User 모델의 id(foreign key) 지정

  ```python
  class User(db.Model): 
    id = db.Column(db.Integer(), primary_key=True) 
    username = db.Column(db.String(255)) 
    password = db.Column(db.String(255)) 
    posts = db.relationship('Post', backref='user', lazy='dynamic') 
  ```

  - lazy: 관계 객체의 로드를 제어하기 위해 사용
    - subquery: 해당 객체가 로드될 때, 관계된 객체를 즉시 불러옴
      - 쿼리 수는 줄지만, 관계가 복잡하고 양이 많을 경우 속도 저하
    - dynamic: 객체에 접근할 때 불러옴(lazy evaluation)
      - 객체가 많고 복잡할 때 유용

  ```python
  >>> user = User.query.get(1)
  >>> user.username
  'faker'
  >>> new_post = Post('post title')
  >>> new_post.user_id = user.id
  >>> db.session.add(new_post)
  >>> db.session.commit()
  >>> user.posts  # user backref = 'posts'
  [<Post 'post title'>]
  >>> new_post.user  # post backref = 'user'
  [<User 'faker'>]
  
  ```

  

**Many-to-many**

- m2m일 경우 db.Table을 이용해 m2m을 위한 보조 테이블을 생성해야 한다.

```python
# db.Table('table_name', db.Colum(), ...)
tags = db.Table('post_tags', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')), 
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')) 
) 
 
class Post(db.Model): 
    ...
    tags = db.relationship( 
        'Tag', 
        secondary=tags, 
        backref=db.backref('posts', lazy='dynamic') 
    ) 
 
class Tag(db.Model): 
    id = db.Column(db.Integer(), primary_key=True) 
    title = db.Column(db.String(255))
```

