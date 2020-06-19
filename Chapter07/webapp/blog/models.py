import datetime
from ..auth.models import User
from .. import mongo


class Comment(mongo.EmbeddedDocument):
    name = mongo.StringField(required=True)
    text = mongo.StringField(required=True)
    date = mongo.DateTimeField(default=datetime.datetime.now())

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


class Post(mongo.Document):
    meta = {'ordering': ['-publish_date']}  # descending

    # mongodb - size & index 설정
    # meta = {
    #     'collection': 'user_posts',
    #     'max_documents': 10000,
    #     'max_size': 2000000,
    #     'indexes': [
    #         'title',
    #         ('title', 'user')
    #     ]
    # }

    title = mongo.StringField(required=True)
    text = mongo.StringField()
    publish_date = mongo.DateTimeField(default=datetime.datetime.now())
    user = mongo.ReferenceField(User)
    comments = mongo.ListField(mongo.EmbeddedDocumentField(Comment))
    tags = mongo.ListField(mongo.StringField())

    def __repr__(self):
        return "<Post '{}'>".format(self.title)
