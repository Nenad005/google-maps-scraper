from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, send
import random
from string import ascii_uppercase
import time

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def loop():
    while True:
        print('sending')
        socketio.emit('message', f'{random.randint(0,1000)}')
        time.sleep(10)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=80)
    loop()