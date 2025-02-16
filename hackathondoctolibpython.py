import pandas as pd
import random
import nltk
from nltk.corpus import wordnet as wn
from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage
import os

#Download WordNet if necessary
nltk.download('wordnet')
nltk.download('omw-1.4')

# Local semantic verification function with WordNet
def is_semantically_offensive(user_text, offensive_words, threshold=0.8):
    """
    Vérifie si un des mots de user_text est sémantiquement lié (via WordNet) à un mot de offensive_words.
    Retourne (True, matched_word) si une correspondance est trouvée, sinon (False, None).
    """
    tokens = user_text.lower().split()  # simple Tokenisation 
    for token in tokens:
        token_synsets = wn.synsets(token)
        if not token_synsets:
            continue
        for offensive_word in offensive_words:
            offensive_synsets = wn.synsets(offensive_word.lower())
            if not offensive_synsets:
                continue
            for ts in token_synsets:
                for osyn in offensive_synsets:
                    similarity = ts.wup_similarity(osyn)
                    if similarity and similarity >= threshold:
                        return True, offensive_word
    return False, None

# Initialize the Mistralai client with the API key given in the documentation
client = Mistral(api_key = os.getenv("API_KEY"))

# Load datasets and generate DataFrame
ultra_chat_dataset = pd.read_parquet('https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k/resolve/main/data/test_gen-00000-of-00001-3d4cd8309148a71f.parquet')
harmful_strings_url = "https://raw.githubusercontent.com/llm-attacks/llm-attacks/main/data/advbench/harmful_strings.csv"
harmful_strings_df = pd.read_csv(harmful_strings_url)
N = 5573
combined_dataset = ultra_chat_dataset['prompt'].tolist()[:N//2] + harmful_strings_df['target'].tolist()[:N//2]
seed = 42
random.seed(seed)
random.shuffle(combined_dataset)
formatted_dataset = [
    {"text": text, "label": "harmful" if text in harmful_strings_df['target'].tolist() else "ultrachat"}
    for text in combined_dataset
]
df = pd.DataFrame(formatted_dataset)
df = df[df["label"] == "harmful"]

def get_embeddings_by_chunks(data, chunk_size):
    chunks = [data[x : x + chunk_size] for x in range(0, len(data), chunk_size)]
    embeddings_response = [
        client.embeddings.create(model="mistral-embed", inputs=c) for c in chunks
    ]
    return [d.embedding for e in embeddings_response for d in e.data]

df["embeddings"] = get_embeddings_by_chunks(df["text"].tolist(), 50)
print(df)
df.to_csv('data.csv', index=False)

# Ask user to enter list of offensive themes
offensive_input = input("Mettez les thèmes à éviter (séparés par des virgules) : ")
offensive_words = [word.strip() for word in offensive_input.split(",") if word.strip()]
print("Liste des thèmes offensants :", offensive_words)

def save_offensive_words():
    """Sauvegarde la liste actuelle des mots offensants dans un fichier."""
    with open("offensive_words.txt", "w") as f:
        f.write("\n".join(offensive_words))

# Prompt system for Mistralai with semantic instructions
system_prompt = (
    "You are a strict moderation assistant specialized in detecting offensive content. "
    "You must analyze user-submitted text and determine whether it contains offensive or inappropriate content. "
    "Consider not only exact matches but also contextual relationships. For example, if the offensive words list includes 'flower' "
    "and the user writes 'poppy' (which is a type of flower), you should consider it offensive and return a response starting with 'Blocked:'.\n\n"
    "Offensive words list: " + ", ".join(offensive_words) + "\n\n"
    "Input: {input}\n"
    "Response:"
)

def run_mistralai_moderation(user_text, model="mistral-large-latest"):
    """
    Envoie une requête à Mistralai en incluant un prompt système qui insiste sur la détection sémantique.
    """
    prompt = system_prompt.format(input=user_text)
    chat_history = [SystemMessage(content=prompt)]
    response = client.chat.complete(
        model=model,
        messages=chat_history
    )
    return response.choices[0].message.content.strip()

print("\nInteractive Moderation System with Semantic Matching.")
print("Commands:")
print("  /add <word>      - Add a word to the offensive list")
print("  /delete <word>   - Remove a word from the offensive list")
print("  /list            - Display all offensive words")
print("  exit             - Quit the program")

# Interactive loop
while True:
    user_input = input("\nEnter a sentence to moderate: ").strip()

    # Command to exit
    if user_input.lower() == "exit":
        print("Exiting moderation system. Saving offensive words...")
        save_offensive_words()
        break

    # Command to add an offensive word
    if user_input.startswith("/add "):
        new_word = user_input.split(" ", 1)[1].strip()
        if new_word:
            if new_word in offensive_words:
                print(f"'{new_word}' is already in the list.")
            else:
                offensive_words.append(new_word)
                save_offensive_words()
                print(f"Added '{new_word}' to the offensive words list.")
        else:
            print("Please provide a valid word to add.")
        continue

    # Command to delete an offensive word
    if user_input.startswith("/delete "):
        word_to_delete = user_input.split(" ", 1)[1].strip()
        if word_to_delete:
            if word_to_delete in offensive_words:
                offensive_words.remove(word_to_delete)
                save_offensive_words()
                print(f"Removed '{word_to_delete}' from the offensive words list.")
            else:
                print(f"'{word_to_delete}' is not in the offensive words list.")
        else:
            print("Please provide a valid word to delete.")
        continue

    # Command to display the list of offensive words
    if user_input == "/list":
        if offensive_words:
            print("Offensive words: " + ", ".join(offensive_words))
        else:
            print("No offensive words in the list.")
        continue

    # Local semantic check before calling Mistralai
    sem_offensive, matched_word = is_semantically_offensive(user_input, offensive_words, threshold=0.8)
    if sem_offensive:
        print(f"Blocked: The input is semantically related to the offensive word '{matched_word}'.")
        # Add harmful statement to list if not already present
        if user_input not in offensive_words:
            offensive_words.append(user_input)
            save_offensive_words()
            print("Harmful declaration added to offensive words list.")
        continue

    # Otherwise, using Mistralai to moderate the text according to the system prompt
    moderation_response = run_mistralai_moderation(user_input)
    print(f"Mistralai's Response: {moderation_response}")
    
    # If Mistralai's response indicates a block, add the entry to the list of offensive words
    if moderation_response.lower().startswith("blocked:"):
        if user_input not in offensive_words:
            offensive_words.append(user_input)
            save_offensive_words()
            print("Harmful declaration added to offensive words list.")
