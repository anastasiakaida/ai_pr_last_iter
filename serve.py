from flask import Flask, request, make_response, jsonify, Response, render_template

import cv2

from backend.src.server.db import Handler
from backend.src.server.json_encoder import AprJsonEncoder
import backend.src.server.converter as converter

from backend.src.recognizer.agent import AgentBuilder, AgentBuilderError
from backend.src.recognizer.enviroment import EnviromentFactory, EnviromentNotFound
from backend.src.recognizer.item import Item
from backend.src.recognizer.image import ImageMongo
from backend.src.recognizer.detector import DETECTOR
from backend.src.recognizer.matcher import MATCHER

import threading
import time

import argparse 

parser = argparse.ArgumentParser(description='Recognizer REST Server')
parser.add_argument(
        '-c', '--camera',
        dest='camera',
        action='store',
        type=int,
        default=0,
        help='camera index'
        )
parser.add_argument(
        '-cw', '--camera-width',
        dest='cwidth',
        action='store',
        type=int,
        default=1280,
        help='camera frame\'s width'
        )
parser.add_argument(
        '-ch', '--camera-height',
        dest='cheight',
        action='store',
        type=int,
        default=720,
        help='camera frame\'s height'
        )
parser.add_argument(
        '-av', '--agent-verbose',
        dest='averbose',
        action='store_true',
        help='create verbose agent'
        )
parser.add_argument(
        '-ans', '--agent-not-smart',
        dest='adumb',
        action='store_true',
        help='create agent which will calculate descriptors and keypoints \
                of object every time'
        )
parser.add_argument(
        '-ad', '--agent-detector',
        dest='adetector',
        choices=DETECTOR,
        default=DETECTOR[3],
        help='detector which agent will use'
        )
parser.add_argument(
        '-am', '--agent-matcher',
        dest='amatcher',
        choices=MATCHER,
        default=MATCHER[2],
        help='matcher which agent will use'
        )

app = Flask(__name__, template_folder='./frontend')
app.json_encoder = AprJsonEncoder
app.url_map.converters['ObjectId'] = converter.ObjectIdConverter
dbhandler = Handler()

agent = None
state_img = None
state_cnt = None
state_timestamp = None

# redirection to frontend
@app.route('/', defaults={'path':''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')

# API
@app.route('/api/stream')
def stream():
    def gen():
        global state_img
        while True:
            time.sleep(0.5)
            retval, jpg = cv2.imencode('.jpg', state_img.copy())
            resp = '--frame\r\n'.encode()
            resp += 'Content-Type: image/jpg\r\n\r\n'.encode()
            resp += jpg.tobytes()
            resp += '\r\n'.encode()
            yield resp
            
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/agent/recognize/image', methods = [ 'GET' ])
def recognizeImage():
    global state_img
    retval, jpg = cv2.imencode('.jpg', state_img.copy())
    response = make_response(jpg.tobytes())
    response.headers['Content-Type'] = 'image/jpg'
    return response

@app.route('/api/agent/recognize/coords', methods = [ 'GET' ])
def recognizeCoords():
    global state_image, state_cntr, state_timestamp
    ic = state['item_cntr']
    st = state['timestamp']
    if item_cntr is None:
        return jsonify({
            'x' : None,
            'y' : None,
            'timestamp' : state_timestamp
            })
    return jsonify({
            'x' : state_cntr.item(0),
            'y' : state_cntr.item(1),
            'timestamp' : state_timestamp.total_seconds()
            })

# id can be 00...00 to set item to None, which will stop recognition
@app.route('/api/agent/set/item/<ObjectId:id>', methods = [ 'GET' ])
def setItem(id):
    global dbhandler
    global agent
    try:
        item_data = dbhandler.find_item_one({ '_id' : id })
        item_image = dbhandler.find_image(item_data['img_id'])
        item = Item(
                item_data['name'],
                ImageMongo(item_image.read()),
                None,
                None,
                str(item_data['_id'])
                )
        agent.set_item(item)
    except:
        agent.set_item(None)

@app.route('/api/items', methods = [ 'GET' ] )
def getItems():
    global dbhandler
    items = dbhandler.find_item({})
    return jsonify(list(items))

@app.route('/api/items/<ObjectId:id>', methods = [ 'GET' ])
def getItem(id):
    global dbhandler
    item = dbhandler.find_item_one( { '_id' : id } )
    return jsonify(item)

@app.route('/api/items', methods = [ 'POST' ] )
def createItem():
    global dbhandler
    name = request.form['name']
    image = request.files['image'] 
    return jsonify(dbhandler.insert_item(name = name, image = image))

@app.route('/api/images/<ObjectId:id>', methods = [ 'GET' ])
def getImage(id):
    global dbhandler
    image = dbhandler.find_image(id)
    response = make_response(image.read())
    response.headers['Content-Type'] = image.content_type
    return response

def agent_loop():
    global agent
    global state_img, state_cntr, state_timestamp
    while True:
        state_img, state_cntr, state_timestamp = agent.run()
        #print(state)

if __name__ == '__main__':
    args = parser.parse_args()

    ab = AgentBuilder()
    agent = ab.get_agent(
            args.averbose,
            args.adumb,
            args.adetector,
            args.amatcher,
            'CAMERA',
            args.camera,
            args.cwidth,
            args.cheight,
            None
            )

    t = threading.Thread(target=agent_loop)
    t.start()
    app.run(debug=True, use_reloader=False, threaded=False, host='0.0.0.0')
