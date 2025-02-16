from flask import Flask, render_template, request, redirect, url_for
from config import Config
from forms import ChatForm
from models import db, ChatMessage

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    form = ChatForm()
    if form.validate_on_submit():
        username = form.username.data
        message = form.message.data
        turn = ChatMessage.get_user_turn(username) + 1
        new_message = ChatMessage(username=username, message=message, turn=turn)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('chat'))
    messages = ChatMessage.query.all()
    return render_template('chat.html', form=form, messages=messages)

@app.route('/chat_list')
def chat_list():
    messages = ChatMessage.query.all()
    return render_template('chat_list.html', messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
