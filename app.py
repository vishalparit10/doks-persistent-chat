# app.py
from flask import Flask, render_template_string, request, jsonify
import redis
import os

app = Flask(__name__)
# The hostname 'redis-service' matches the Kubernetes Service name we'll create later
r = redis.Redis(host='redis-service', port=6379, decode_responses=True)

HTML = """
<!DOCTYPE html>
<html>
<head><title>DOKS Chat</title></head>
<body>
    <div id="messages" style="border:1px solid #ccc; height:200px; overflow-y:scroll;"></div>
    <input id="msg" type="text"> <button onclick="send()">Send</button>
    <script>
        function send() {
            const msg = document.getElementById('msg').value;
            fetch('/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
        }
        setInterval(() => {
            fetch('/messages').then(res => res.json()).then(data => {
                document.getElementById('messages').innerHTML = data.join('<br>');
            });
        }, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/send', methods=['POST'])
def send():
    msg = request.json.get('message')
    r.rpush('chat_history', msg)
    r.ltrim('chat_history', -20, -1) # Keep only last 20 messages (ephemeral)
    return jsonify(success=True)

@app.route('/messages')
def get_messages():
    return jsonify(r.lrange('chat_history', 0, -1))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
