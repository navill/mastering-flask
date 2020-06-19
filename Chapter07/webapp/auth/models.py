from . import bcrypt, AnonymousUserMixin
from .. import mongo


class Role(mongo.Document):
    name = mongo.StringField(max_length=64, required=True, unique=True)
    description = mongo.StringField()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name


class User(mongo.Document):
    username = mongo.StringField(required=True, unique=True)
    password = mongo.BinaryField(required=True)

    roles = mongo.ListField(mongo.ReferenceField(Role))

    def __unicode__(self):
        return '<User {}>'.format(self.username)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def has_role(self, name):
        for role in self.roles:
            if role.name == name:
                return True
        return False

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        user = User.objects(username=self.username).get()
        return bcrypt.check_password_hash(user.password, password)

    @property
    def is_authenticated(self):
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
