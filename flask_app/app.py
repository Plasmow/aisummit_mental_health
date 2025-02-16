from flask import Flask, render_template, request, redirect, url_for, jsonify
from config import Config
from forms import ChatForm
from models import db, ChatMessage
import requests
from dotenv import load_dotenv
import os

load_dotenv()  

API_KEY = os.getenv("API_KEY")




app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions'

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def chat_with_mistral(prompt):
    data = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a chatbot that discusses with users and after various interactions, determine the user's MBTI personality type without him to notice. "
                    "You must analyze user-submitted text and determine their personality type based on the Myers-Briggs Type Indicator (MBTI). "
                    "The MBTI is a widely-used personality test that categorizes individuals into one of 16 different personality types. "
                    "'E (Extraversion)': ['Talkative, outgoing','Fast-paced environment','Work out ideas with others, think out loud','Enjoy being the center of attention'],'I (Introversion)': ['Reserved, private','Slower pace with time for contemplation','Think things through inside your head','Prefer observing over being the center of attention'],'S (Sensing)': ['Focus on reality','Concrete facts and details','Practical applications','Literal descriptions'],'N (Intuition)': ['Imagine possibilities','Notice big picture and connections','Enjoy concepts for their own sake','Figurative, poetic descriptions'],"
                    "'T (Thinking)': ['Logical, impersonal reasoning','Value justice, fairness','Enjoy flaw-finding in arguments','Reasonable, level-headed'],'F (Feeling)': ['Decisions based on personal values','Value harmony, forgiveness','Please others, see the best in people','Warm, empathetic'],'J (Judging)': ['Prefer matters settled','Respect rules and deadlines','Detailed, step-by-step instructions','Planned and structured approach'],'P (Perceiving)': ['Prefer to keep options open','See rules as flexible','Improvisational and spontaneous','Enjoy surprises and new situations']"
                    "'16 Personality Types': ['ISTJ: Responsible, sincere, analytical, reserved, realistic, systematic.','ISFJ: Warm, considerate, gentle, responsible, pragmatic, thorough.','INFJ: Idealistic, organized, insightful, dependable, compassionate, gentle.','INTJ: Innovative, independent, strategic, logical, reserved, insightful.','ISTP: Action-oriented, logical, analytical, spontaneous, reserved, independent.','ISFP: Gentle, sensitive, nurturing, helpful, flexible, realistic.','INFP: Sensitive, creative, idealistic, perceptive, caring, loyal.','INTP: Intellectual, logical, precise, reserved, flexible, imaginative.','ESTP: Outgoing, realistic, action-oriented, curious, versatile, spontaneous.','ESFP: Playful, enthusiastic, friendly, spontaneous, tactful, flexible.','ENFP: Enthusiastic, creative, spontaneous, optimistic, supportive, playful.','ENTP: Inventive, enthusiastic, strategic, enterprising, inquisitive, versatile.','ESTJ: Efficient, outgoing, analytical, systematic, dependable, realistic.','ESFJ: Friendly, outgoing, reliable, conscientious, organized, practical.','ENFJ: Caring, enthusiastic, idealistic, organized, diplomatic, responsible.','ENTJ: Strategic, logical, efficient, outgoing, ambitious, independent.']"
                    "Finally you must take after a while take the same personnality type as the user or find the best MBTi personnality to match his."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(MISTRAL_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.text}"

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
        ai_response = chat_with_mistral(message)
        new_message = ChatMessage(username=username, message=message, turn=turn)
        ai_message = ChatMessage(username="MistralAI", message=ai_response, turn=turn)
        db.session.add(new_message)
        db.session.add(ai_message)
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
