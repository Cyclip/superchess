from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import eventlet
from eventlet import wsgi
import json

from chess import chess
import engine
import engine_utils

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app)

sessions = {
    # 'ssid': Board
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/play/<string:kind>")
def play(kind):
    if kind not in ['local', 'bot']:
        return render_template('index.html')

    return render_template('play.html', kind=kind)

@socketio.on('connect')
def on_connect_event():
    print("Connected")
    emit('connected')

@socketio.on('request_board')
def on_request_board_event(data):
    print(f"Requesting board: {data}")
    # Always rewrite the board
    ssid = data['ssid']
    sessions[ssid] = chess.ChessBoard()

    board = sessions[ssid]
    emit('board', board.pieces_to_json())

@socketio.on('get_legal_moves')
def on_get_legal_moves_event(data):
    print(f"Requesting legal moves: {data}")
    # Data must contain ssid and pos
    ssid = data['ssid']
    pos = data['pos']

    board = sessions[ssid]
    emit('legal_moves', board.get_legal_moves(pos))

@socketio.on('move_piece')
def on_move_piece_event(data):
    print(f"Moving piece: {data}")
    # Data must contain ssid, from, and to
    ssid = data['ssid']
    start_pos = data['from']
    end_pos = data['to']

    board = sessions[ssid]
    board.move_piece(start_pos, end_pos)
    board.update_game_state()

    # instead of sending the whole board, re-send the from and to positions
    # and the piece that was moved
    emit('move_piece', {
        'from': start_pos,
        'to': end_pos,
        'piece': board.get_piece(end_pos).to_json()
    })

    # Check if the game is over
    if board.game_over:
        emit('game_over', {
            "outcome": board.outcome
        })
        # Remove the session from the sessions dict
        del sessions[ssid]
    else:
        # Send evaluation
        emit('evaluation', {
            "evaluation": engine_utils.evaluate_board(board)
        })

@socketio.on('bot_move')
def on_bot_move_event(data):
    print(f"Bot moving piece: {data}")
    # Data must contain ssid
    ssid = data['ssid']
    board = sessions[ssid]

    # Get the best move
    move = engine.get_move(board)

    # Move the piece
    board.move_piece(move[0], move[1])
    board.update_game_state()

    # instead of sending the whole board, re-send the from and to positions
    # and the piece that was moved
    emit('move_piece', {
        'from': move[0],
        'to': move[1],
        'piece': board.get_piece(move[1]).to_json()
    })

    # Check if the game is over
    if board.game_over:
        emit('game_over', {
            "outcome": board.outcome
        })
        # Remove the session from the sessions dict
        del sessions[ssid]
    else:
        # Send evaluation
        emit('evaluation', {
            "evaluation": engine.evaluate_board(board)
        })

@socketio.on('disconnect')
def on_disconnect_event():
    print("Disconnected")
    # Remove the session from the sessions dict


if __name__ == '__main__':
    # app.run(debug=True)
    wsgi.server(eventlet.listen(('', 5000)), app)