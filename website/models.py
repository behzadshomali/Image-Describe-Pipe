from flask_login import UserMixin

class User(UserMixin):
    # id = db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(150), unique=True)
    # username = db.Column(db.String(150), unique=True)
    # password = db.Column(db.String(150))
    # date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # posts = db.relationship('Post', backref='user', passive_deletes=True)
    id = 5
    email = 'behzad@yahoo.com'