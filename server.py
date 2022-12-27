from flask import Flask, render_template
from flask_sock import Sock
import eventlet
from eventlet import wsgi

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
sock = Sock(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/play/<string:kind>")
def play(kind):
    return render_template('play.html', kind=kind)

@sock.route('/echo')
def echo(ws):
    # echo once
    message = ws.receive()
    ws.send(message)

if __name__ == '__main__':
    app.run(debug=True)
    # wsgi.server(eventlet.listen(('', 5000)), app)