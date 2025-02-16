async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value;
    if (message.trim() !== '') {
        const response = await fetch('/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        const messagesDiv = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        messagesDiv.appendChild(messageElement);
        input.value = '';
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}