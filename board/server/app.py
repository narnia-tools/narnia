import threading
from os.path import normpath, join, dirname, abspath

from flask import Flask
from flask import send_from_directory
from flask import render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit, join_room

app_root = normpath(join(dirname(abspath(__file__)), '../client/'))
app = Flask(__name__, root_path=app_root, template_folder=app_root)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)


@app.route("/")
def hello():
    message = "Hello, World"
    return render_template('index.html', message=message)

@app.route('/node_modules/', defaults={'path': ''})
@app.route('/node_modules/<path:path>')
def base_static(path):
    return send_from_directory(app.root_path + '/node_modules/', path)

@socketio.on('board connect')
def board_connect():
    print('Joined Room! :) ')
    join_room('board')
    push_data('Connected Room')

def push_data(x):
    print('-->', x)
    emit('data', x, room='board')

# @socketio.on('my event')
# def on_my_event(data):
#     send_accuracy(data)


@socketio.on('push data')
def on_my_event(data):

    push_data(data)



if __name__ == '__main__':

    app.run()
