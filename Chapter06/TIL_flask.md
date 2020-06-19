# Flask TIL - Chapter06

### Authentication

- [Nginx authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/)
- Flask authentication



### 인증 종류

**Basic auth - 단순하지만 안전하지 않은 인증 코드**

```python
def authenticate(username, password):
    return username == 'admin' and password == 'password'

@app.route('/basic-auth-page')
def basic_auth_page():
    auth = request.authorization
		if not auth or not authenticate(auth.username,auth.password)
        return Response('Login with username/password', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})
    return render_template('some_page.html')
```

**Remote-user auth**

**LDAP(lightweight directory access protocol) auth**

**DB User model auth**

**OpenID and [OAuth](https://flask-dance.readthedocs.io/en/latest/how-oauth-works.html#oauth-2)**



### Flask-Login 

- 인증이 필요한 User model에 아래의 코드가 추가 된다.

  ```python
  # auth/__init__.py
  
  ...
  # for guest
  class BlogAnonymous(AnonymousUserMixin):
      def __init__(self):
          self.username = 'Guest'
          
  
  # auth/models.py        
  class User(db.Model):
      ...
  
      @property
      def is_authenticated(self):
          # guest는 AnonymousUserMixin를 상속받음
          if isinstance(self, AnonymousUserMixin):
              return False
          else:
              return True
  
      @property
      def is_active(self):
          return True
  
      @property
      def is_anonymous(self):
          if isinstance(self, AnonymousUserMixin):
              return True
          else:
              return False
  
      def get_id(self):
          return str(self.id)
  
  ```

  - is_authenticated: 유저의 인증 여부 확인
  - is_active: active 유저인지 확인
  - is_anonymous: 게스트 유저의 접근 여부
  - get_id: 유저 아이디







### Role-based access control (RBAC)

```python
roles = db.Table(
    'role_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

```

- m2m으로 User와 Role 모델을 연결한다.

```python
class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    ...
    
    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('users', lazy='dynamic')  #User에서 Role에 대한 역참조
    )
    
    def has_role(self, name):  # template에서 사용됨
        for role in self.roles:
          if role.name == name:
            return True
        return False
```



