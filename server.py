from flask import Flask, render_template
from flask_sock import Sock
import eventlet
from eventlet import wsgi
import json

from chess import chess

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
sock = Sock(app)

sessions = {
    # 'ssid': Board
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/play/<string:kind>")
def play(kind):
    return render_template('play.html', kind=kind)

@sock.route('/board')
def board_mech(ws):
    while True:
        message = json.loads(ws.receive())
        ssid = message['ssid']
        
        if ssid not in sessions:
            sessions[ssid] = chess.ChessBoard()
        
        board = sessions[ssid]

        match message['type']:
            case 'request_board':
                ws.send(json.dumps({'type': 'board', 'data': board.pieces_to_json()}))
            case 'get_legal_moves':
                pos = message['data']['pos']
                ws.send(json.dumps({'type': 'legal_moves', 'data': board.get_legal_moves(pos)}))
            case 'move_piece':
                print(f"Received move_piece request: {message['data']}")
                start_pos = message['data']['from']
                end_pos = message['data']['to']
                board.move_piece(start_pos, end_pos)

                # instead of sending the whole board, re-send the from and to positions
                # and the piece that was moved
                ws.send(json.dumps({'type': 'move_piece', 'data': {
                    'from': start_pos,
                    'to': end_pos,
                    'piece': board.get_piece(end_pos).to_json()
                }}))
            case _:
                ws.send(json.dumps({'type': 'error', 'data': 'Invalid request'}))

if __name__ == '__main__':
    app.run(debug=True)
    # wsgi.server(eventlet.listen(('', 5000)), app)