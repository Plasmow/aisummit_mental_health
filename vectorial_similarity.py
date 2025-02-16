import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage
import time

# Initialiser le client Mistral avec votre API key
client = Mistral(api_key = os.getenv("API_KEY"))

def get_bot_response(history, model="mistral-large-latest", temperature=0.7):
    """
    Envoie l'historique de la conversation au modèle Mistral et retourne la réponse du chatbot.
    """
    response = client.chat.complete(
        model=model,
        messages=history,
        # Vous pouvez ajuster la température si besoin.
        # temperature=temperature  
    )
    return response.choices[0].message.content.strip()

def get_embeddings(texts, model="mistral-embed"):
    """
    Obtenir les embeddings pour une liste de textes via le modèle d'embeddings de Mistral.
    Retourne une liste de vecteurs (numpy arrays).
    """
    response = client.embeddings.create(model=model, inputs=texts)
    embeddings = []
    for data_item in response.data:
        embeddings.append(np.array(data_item.embedding))
    return embeddings

def simulate_conversation(num_turns=3):
    """
    Simule une conversation entre deux chatbots.
    Retourne deux listes contenant les messages générés par Bot A et Bot B respectivement.
    """
    # Message système pour fournir des consignes aux chatbots.
    system_message = SystemMessage(content="You are a friendly chatbot engaged in a natural conversation. Please respond naturally and respectfully.")

    # Initialiser l'historique de chaque bot (nous utilisons la même consigne pour les deux)
    bot_a_history = [system_message]
    bot_b_history = [system_message]
    
    # Début de la conversation : Bot A initie la conversation.
    bot_a_initial = "Hello, how are you today?"
    bot_a_history.append(UserMessage(content=bot_a_initial))
    bot_a_response = get_bot_response(bot_a_history)
    print("Bot A: " + bot_a_initial)
    print("Bot A (response): " + bot_a_response)
    
    # Stocker les échanges dans des listes
    bot_a_messages = [bot_a_initial, bot_a_response]
    bot_b_messages = []
    
    # Simuler les échanges en alternant les réponses
    for turn in range(num_turns):
        # Bot B reçoit le dernier message de Bot A et y répond.
        bot_b_history.append(UserMessage(content=bot_a_response))
        bot_b_response = get_bot_response(bot_b_history)
        bot_b_messages.append(bot_b_response)
        print(f"Bot B (turn {turn+1} response): " + bot_b_response)
        time.sleep(1)  # petite pause pour éviter les appels trop rapides
        
        # Bot A reçoit la réponse de Bot B et y répond.
        bot_a_history.append(UserMessage(content=bot_b_response))
        bot_a_response = get_bot_response(bot_a_history)
        bot_a_messages.append(bot_a_response)
        print(f"Bot A (turn {turn+1} response): " + bot_a_response)
        time.sleep(1)
        
    return bot_a_messages, bot_b_messages

# Simuler la conversation
bot_a_msgs, bot_b_msgs = simulate_conversation(num_turns=3)

# Calculer la similarité vectorielle entre chaque paire d'échanges (Bot A et Bot B)
print("\nCalcul de la similarité vectorielle entre les échanges :")
all_similarities = []
for a_msg, b_msg in zip(bot_a_msgs, bot_b_msgs):
    # Obtenir les embeddings pour le message de Bot A et celui de Bot B
    embeddings = get_embeddings([a_msg, b_msg])
    # Calculer la similarité cosinus entre les deux vecteurs
    sim = cosine_similarity(embeddings[0].reshape(1, -1), embeddings[1].reshape(1, -1))[0][0]
    all_similarities.append(sim)
    print(f"Bot A: {a_msg}\nBot B: {b_msg}\nSimilarity: {sim:.3f}\n")

if all_similarities:
    avg_sim = sum(all_similarities) / len(all_similarities)
    print(f"Average similarity between exchanges: {avg_sim:.3f}")
