from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    turn = db.Column(db.Integer, nullable=False)

    @staticmethod
    def get_user_turn(username):
        return db.session.query(db.func.max(ChatMessage.turn)).filter_by(username=username).scalar() or 0
