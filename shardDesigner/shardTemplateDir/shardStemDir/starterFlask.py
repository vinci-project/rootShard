import sys, os
import json
import redis
import shutil

from crypto.vncCrypto import VncCrypto
from crypto.cryptoFernet import cryptoFernet

from datetime import datetime, date, time
from random import randint
import psutil
import uuid
from werkzeug.utils import secure_filename

#=================================== FLASK ZONE
from flask import Flask, abort, request, Response, send_from_directory

class FlaskStarter():
    def __init__(self):
        self.app = Flask(__name__)
        self.cryptor = VncCrypto()

        @self.app.route('/img/<path:path>')
        def send_img(path):
            return send_from_directory('static/img', path)

        @self.app.route('/js/<path:path>')
        def send_js(path):
            return send_from_directory('static/js', path)

        @self.app.route('/css/<path:path>')
        def send_css(path):
            return send_from_directory('static/css', path)

        @self.app.route('/static/<path:path>')
        def send_html(path):
            return send_from_directory('static', path)

        @self.app.route('/start/generatePair', methods=['GET','POST'])
        def generatePair():
            if not request:
                abort(400)

            self.cryptor.generateKeys()

            return json.dumps({"PRIVATE": self.cryptor.getPrivateKey(), "PUBLIC": self.cryptor.getPublicKey()}, separators=(',', ':'))

        @self.app.route('/start/setPrivate', methods=['GET','POST'])
        def setPrivate():
            if not request:
                abort(400)

            private = request.args.get('private')
            password = request.args.get('password')

            crf = cryptoFernet(password)
            token = crf.crypt(private)
            pFile = open("PRIVATE", "w")
            pFile.write(token.decode())

            return json.dumps({}, separators=(',', ':'))

        @self.app.route('/start/startSlave', methods=['GET','POST'])
        def startSlave():
            if not request:
                abort(400)

            password = request.args.get('password')
            os.system("slaveNode.py " + password)
            os.system("<%START BINARY COMMAND%>")


            return json.dumps({"START": "OK"}, separators=(',', ':'))

        @self.app.route('/start/getPrivateStatus', methods=['GET','POST'])
        def getPrivateStatus():
            if not request:
                abort(400)

            if os.path.exists("PRIVATE"):
                return json.dumps({"PRIVATE": True}, separators=(',', ':'))
            else:
                return json.dumps({"PRIVATE": False}, separators=(',', ':'))


    def run(self):
        self.app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    flask = FlaskStarter()
    flask.run()
