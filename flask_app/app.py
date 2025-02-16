from flask import Flask, render_template, request, redirect, url_for, jsonify
from config import Config
from forms import ChatForm
from models import db, ChatMessage
import requests
from dotenv import load_dotenv
import os
import random

load_dotenv()

API_KEY = os.getenv("API_KEY")
MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions'

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Dictionnaire des prompts système pour chaque type MBTI
prompts_systeme = {
    "INTJ": "Tu es un chatbot au tempérament INTJ, analytique et stratégique.",
    "ENTP": "Tu es un chatbot au tempérament ENTP, inventif et débattu.",
    "ENTJ": "Tu es un chatbot au tempérament ENTJ, leader et déterminé.",
    "INTP": "Tu es un chatbot au tempérament INTP, curieux et logique.",
    "ENFP": "Tu es un chatbot au tempérament ENFP, enthousiaste et créatif.",
    "ENFJ": "Tu es un chatbot au tempérament ENFJ, empathique et inspirant.",
    "ISTJ": "Tu es un chatbot au tempérament ISTJ, responsable et organisé.",
    "ISFJ": "Tu es un chatbot au tempérament ISFJ, loyal et attentionné.",
    "INFJ": "Tu es un chatbot au tempérament INFJ, idéaliste et perspicace.",
    "ISTP": "Tu es un chatbot au tempérament ISTP, pragmatique et réservé.",
    "ISFP": "Tu es un chatbot au tempérament ISFP, artistique et sensible.",
    "INFP": "Tu es un chatbot au tempérament INFP, idéaliste et loyal.",
    "ESTP": "Tu es un chatbot au tempérament ESTP, énergique et aventureux.",
    "ESFP": "Tu es un chatbot au tempérament ESFP, enthousiaste et sociable.",
    "ESTJ": "Tu es un chatbot au tempérament ESTJ, efficace et pragmatique.",
    "ESFJ": "Tu es un chatbot au tempérament ESFJ, chaleureux et coopératif."
}

# Dictionnaire de compatibilité MBTI pour choisir un ami chatbot compatible
compatibilite_mbti = {
    "INTJ": ["ENTP", "ENTJ", "INTP"],
    "ENTP": ["INTJ", "INFJ", "INTP"],
    "INFJ": ["ENFP", "ENFJ", "INTJ"],
    "ENFP": ["INFJ", "INTJ", "ENTP"],
    "ISTJ": ["ESFP", "ESTP", "ISFJ"],
    "ESTJ": ["ISFP", "ISTP", "ESFJ"],
    "ISFJ": ["ESFP", "ESTP", "ISTJ"],
    "ESFJ": ["ISFP", "ISTP", "ESTJ"],
    "INTP": ["ENTJ", "ENTP", "INTJ"],
    "ENTJ": ["INTP", "INTJ", "ENTP"],
    "INFP": ["ENFJ", "INFJ", "ENFP"],
    "ENFJ": ["INFP", "INFJ", "ENFP"],
    "ISTP": ["ESFJ", "ESTJ", "ISFP"],
    "ESTP": ["ISFJ", "ISTJ", "ESFP"],
    "ISFP": ["ESFJ", "ESTJ", "ISTP"],
    "ESFP": ["ISFJ", "ISTJ", "ESTP"]
}

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

def interroger_mistral(messages):
    data = {
        "model": "mistral-large-latest",
        "messages": messages,
        "temperature": 0.7
    }
    response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Erreur : {response.text}"

def chat_with_mistral(user_message):
    messages = [{"role": "user", "content": user_message}]
    return interroger_mistral(messages)

def hidden_analysis(conversation_history):
    hidden_prompt = (
        "Analyse la conversation ci-dessus et déduis, de manière concise, "
        "le type de personnalité MBTI le plus probable de l'utilisateur (par exemple INTJ, INTP, etc.). "
        "Réponds uniquement par l'abréviation du type sans aucun commentaire."
    )
    messages_for_analysis = conversation_history.copy()
    messages_for_analysis.append({"role": "system", "content": hidden_prompt})
    result = interroger_mistral(messages_for_analysis)
    return result.strip()

def friend_conversation(friend_name, friend_prompt):
    print(f"\n--- Nouvelle conversation avec {friend_name} ---\n")
    messages = [{"role": "system", "content": friend_prompt}]
    print(f"{friend_name} : Salut, je suis {friend_name}. Comment puis-je t'aider aujourd'hui ?")
    while True:
        user_input = input("Vous : ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"{friend_name} : Au revoir !")
            break
        messages.append({"role": "user", "content": user_input})
        reponse = interroger_mistral(messages)
        print(f"{friend_name} : {reponse}")
        messages.append({"role": "assistant", "content": reponse})

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/analyze_mbti', methods=['POST'])
def analyze_mbti():
    conversation_history = request.json.get('conversation_history', [])
    mbti_type = hidden_analysis(conversation_history)
    return jsonify({"mbti_type": mbti_type})

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
        
        # Analyze MBTI type after the chat
        conversation_history = [{"role": "user", "content": message}, {"role": "assistant", "content": ai_response}]
        mbti_type = hidden_analysis(conversation_history)
        return redirect(url_for('chat', mbti_type=mbti_type))
    
    messages = ChatMessage.query.all()
    mbti_type = request.args.get('mbti_type', None)
    return render_template('chat.html', form=form, messages=messages, mbti_type=mbti_type)

@app.route('/chat_list')
def chat_list():
    messages = ChatMessage.query.all()
    return render_template('chat_list.html', messages=messages)

if __name__ == '__main__':
    app.run(debug=True)