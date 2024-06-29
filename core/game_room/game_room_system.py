from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for rooms (replace with database in production)
rooms = {}

class GameRoom:
    def __init__(self, room_id, host_id, max_players=4):
        self.room_id = room_id
        self.host_id = host_id
        self.players = [host_id]
        self.max_players = max_players
        self.created_at = datetime.utcnow()
        self.game_state = "waiting"  # waiting, playing, finished

@app.route('/create_room', methods=['POST'])
def create_room():
    host_id = request.json['host_id']
    room_id = f"room_{len(rooms) + 1}"
    new_room = GameRoom(room_id, host_id)
    rooms[room_id] = new_room
    return jsonify({"room_id": room_id, "message": "Room created successfully"})

@app.route('/join_room', methods=['POST'])
def join_room_http():
    user_id = request.json['user_id']
    room_id = request.json['room_id']
    
    if room_id not in rooms:
        return jsonify({"error": "Room not found"}), 404
    
    room = rooms[room_id]
    if len(room.players) >= room.max_players:
        return jsonify({"error": "Room is full"}), 400
    
    room.players.append(user_id)
    return jsonify({"message": "Joined room successfully"})

@app.route('/list_rooms', methods=['GET'])
def list_rooms():
    room_list = [{"room_id": room.room_id, "players": len(room.players), "max_players": room.max_players}
                 for room in rooms.values()]
    return jsonify(room_list)

@socketio.on('join')
def on_join(data):
    user_id = data['user_id']
    room_id = data['room_id']
    join_room(room_id)
    emit('user_joined', {'user_id': user_id}, room=room_id)

@socketio.on('leave')
def on_leave(data):
    user_id = data['user_id']
    room_id = data['room_id']
    leave_room(room_id)
    emit('user_left', {'user_id': user_id}, room=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)