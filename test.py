from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, send
import random
from string import ascii_uppercase

app = Flask(__name__)
socketio = SocketIO(app)

if __name__ == "__main__":
    socketio.run(app, debug=True)