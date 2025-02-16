import requests
import os
api_key = os.getenv("API_KEY")
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("API_KEY")


# API URL
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# Query headers
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Field for prompting the AI instruction
role_instruction = (
    "Tu es un assistant virtuel qui pose des questions progressivement en réagissant à mes réponses de manière intéressée. "
    "Très amical mais pas trop pompeux. Tu cherches à en apprendre plus sur moi et mon état de santé, si j'ai déjà eu des pensées suicidaires, "
    "des inquiétudes vis-à-vis d'un complexe, ou si je me sens isolé. Ne sois pas trop direct, adopte une approche douce et subtile, "
    "et fais des réponses courtes (max 2 lignes). Arrête-toi naturellement quand tu as assez d'informations."
)

# Initial message
initial_message = "Comment allez-vous?"

# Converseation History
conversation_history = [
    {"role": "system", "content": role_instruction},
    {"role": "assistant", "content": initial_message}
]

# Store questions asked by the AI
questions_asked = [initial_message]

# Store the user responses
user_responses = []

# Counter for sensitive subjects
sensitive_topics_count = 0
sensitive_keywords = ["suicide", "complexe", "isolement", "inquiétude"]

def chat_with_mistral(prompt):
    conversation_history.append({"role": "user", "content": prompt})
    data = {
        "model": "mistral-large-latest",  
        "messages": conversation_history,
        "temperature": 0.7
    }

    # Request
    response = requests.post(MISTRAL_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        conversation_history.append({"role": "assistant", "content": ai_response})
        questions_asked.append(ai_response)
        return ai_response
    else:
        return f"Erreur : {response.text}"

print("Chatbot Mistral AI (tape 'exit' pour quitter)")
print(f"Mistral: {initial_message}")

while True:
    user_input = input("Vous: ")
    if user_input.lower() == "exit":
        break
    
    user_responses.append(user_input)
    response = chat_with_mistral(user_input)
    print(f"Mistral: {response}")

    # Check if enough information has been gathered
    if any(keyword in user_input.lower() for keyword in sensitive_keywords):
        sensitive_topics_count += 1

    if sensitive_topics_count >= 3:  # Threshold for ending the conversation
        print("Mistral: Merci pour vos réponses. Prenez soin de vous.")
        break

# Display questions asked and user answers
print("\nQuestions posées par l'IA:")
for question in questions_asked:
    print(f"- {question}")

print("\nRéponses de l'utilisateur:")
for response in user_responses:
    print(f"- {response}")
