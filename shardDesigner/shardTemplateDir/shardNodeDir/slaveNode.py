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
from flask import Flask, abort, request, Response


class FlaskWorker():
    def __init__(self, privateKey):
        self.app = Flask(__name__)
        self.cryptor = VncCrypto()
        self.cryptor.setPrivateKey(privateKey)
        self.dataFieldsMas = <%FIELDS%>
        self.stemIP = "<%STEMIP%>"
        self.stemPK = "<%STEMPK%>"
        self.redis_host = os.getenv("REDIS_PORT_6379_TCP_ADDR") or 'localhost'
        self.redis_port = os.getenv("REDIS_PORT_6379_TCP_PORT") or '6379'
        self.redis = redis.StrictRedis(self.redis_host, self.redis_port, db=2)

        @self.app.route('/shard/getStatData', methods=['GET','POST'])
        def saveMapElement():
            if not request:
                abort(400)

            jsond = {}
            for field in self.dataFieldsMas:
                if self.redis.get(field) is not None:
                    jsond.update({field: self.redis.get(field)})

            jsonstr = json.dumps(jsond)
            sign = self.cryptor.signMessage(jsonstr)

            return json.dumps({"DATA": jsond,"SIGNATURE": sign}, separators=(',', ':'))

    def run(self):
        self.app.run(host='0.0.0.0', port=5005)



class FlaskStarter():
    def __init__(self):
        self.app = Flask(__name__)
        self.cryptor = VncCrypto()

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

            return json.dumps({"PRIVATE": self.cryptor.getPrivateKey(), "PUBLIC": self.cryptor.getPublicKey()}, separators=(',', ':'))

    def run(self):
        self.app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Need 2 attributes, receive ", len(sys.argv))
        exit(1)

    crf = cryptoFernet(sys.argv[1])
    pFile = open("PRIVATE", "r")
    token = pFile.read().encode()
    private = crf.decrypt(token).decode()

    flask = FlaskWorker(private)

    print("!!!!NODE RUN!!!!")

    flask.run()
