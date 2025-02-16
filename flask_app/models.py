from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    turn = db.Column(db.Integer, nullable=False)
    
    def __str__(self):
        return f"{self.username}, {self.message}, {self.turn}"

    @staticmethod
    def get_conversation_history(username):
        return ChatMessage.query.filter_by(username=username).order_by(ChatMessage.turn).all()

    @staticmethod
    def get_user_turn(username):
        last_message = ChatMessage.query.filter_by(username=username).order_by(ChatMessage.turn.desc()).first()
        return last_message.turn if last_message else 0