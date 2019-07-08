import sys, os
import json,time
import redis
import shutil

from datetime import datetime, date, time
from random import randint
import psutil
import uuid
from werkzeug.utils import secure_filename
import zipfile
import py_compile
from vncCrypto import VncCrypto
#=================================== FLASK ZONE
from flask import Flask, abort, request, Response, send_from_directory
#=================================== EMAIL ZONE
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId

class emailSender():
    def __init__(self):
        self.myEmail = 'no-reply@vncsphere.net'
        self.username = 'no-reply@vncsphere.net'
        self.password = 'LtcSh8qQkqZYJ3tewDVnKZQ8jRYPux'

    def sendEmailConfirm(self, email):
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg['From'] = self.myEmail
        msg['To'] = email

        html = """
        <!doctype html>
        <html>
            <head style = 'border:solid 1px maroon;'>
                <h2>Welcome to the ROOT Shard system!</h2>
                <h3>This e-mail address was specified as a contact on the portal pvm.vncsphere.net in the "Registration" section. To confirm, click on the link below.</h3>
            </head>
        <body>
            <table width="100%" border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td>
                  <table border="0" cellspacing="0" cellpadding="0">
                    <tr>
                      <td align="center" style="border-radius: 3px;" bgcolor="#e9703e"><a href="http://vncsphere.net" target="_blank" style="font-size: 16px; font-family: Helvetica, Arial, sans-serif; color: #ffffff; text-decoration: none; text-decoration: none;border-radius: 3px; padding: 12px 18px; border: 1px solid #e9703e; display: inline-block;">EMAIL CONFIRM</a></td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
        </body>
        </html>
        """

        part = MIMEText(html, 'html')
        msg.attach(part)
        server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
        server.ehlo()
        server.login(self.username, self.password)
        server.sendmail(self.myEmail, email, msg.as_string())
        server.quit()

class FlaskWorker():
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 + 1# 16 Mb - max binary content size
        self.redis_host = os.getenv("REDIS_PORT_6379_TCP_ADDR") or 'localhost'
        self.redis_port = os.getenv("REDIS_PORT_6379_TCP_PORT") or '6379'
        self.redis = redis.StrictRedis(self.redis_host, self.redis_port, db=2)
        self.cryptor = VncCrypto()
        self.cryptor.generateKeys()

        self.mongo_host = os.getenv("MONGO_PORT_27017_TCP_ADDR") or 'localhost'
        self.mongo_port = os.getenv("MONGO_PORT_27017_TCP_PORT") or 27017
        self.mongo_conn = MongoClient(self.mongo_host, self.mongo_port)
        self.mongo = self.mongo_conn.rootShard
        self.mongo_conn.drop_database(self.mongo)  # CLEAR MONGODB VNCSPHERE DATABASE

        @self.app.route('/img/<path:path>')
        def send_img(path):
            return send_from_directory('web/img', path)

        @self.app.route('/js/<path:path>')
        def send_js(path):
            return send_from_directory('web/js', path)

        @self.app.route('/css/<path:path>')
        def send_css(path):
            return send_from_directory('web/css', path)

        @self.app.route('/<path:path>')
        def send_html(path):
            print(path)
            return send_from_directory('web', path)

        @self.app.route('/r/testRootAPI', methods=['GET','POST']) # TEST DB STRUCT FOR DEVELOP GO API
        def testRootAPI():
            if not request:
                abort(400)

            print(self.mongo["SHARD LIST"].save({"NAME": "SUPER SHARD", "OWNER": "SUPER OWNER", "INFO": "SUPER INFO", "STEMIP": "SUPER STEM IP ADDRESS"}))
            print(self.mongo["SHARD NODES LIST"].save({"NAME": "SUPER SHARD NODE", "SHARD ID": 1735262821, "NODE IP": "127.0.0.2", "NODE TYPE": "STANDART 1"}))
            print(self.mongo["SHARD NODES LIST"].save({"NAME": "SUPER SHARD NODE", "SHARD ID": 1735262821, "NODE IP": "127.0.0.3", "NODE TYPE": "STANDART 2"}))
            print(self.mongo["SHARD NODES LIST"].save({"NAME": "SUPER SHARD NODE", "SHARD ID": 1735262821, "NODE IP": "127.0.0.4", "NODE TYPE": "STANDART 2"}))
            print(self.mongo["SHARD BLOCKCHAIN HEIGHT"].save({"SHARD ID": 1735262821, "BHEIGHT": 254, "LAST HASH": "SUPER PUPER HASH"}))
            print(self.mongo["SHARD BLOCKCHAIN HASH LIST"].save({"SHARD ID": 1735262821, "BHEIGHT": 100, "BLOCK HASH": "SUPER BLOCK HASH"}))
            print(self.mongo["SHARD BLOCKCHAIN HASH LIST"].save({"SHARD ID": 1735262821, "BHEIGHT": 101, "BLOCK HASH": "SUPER BLOCK HASH"}))
            print(self.mongo["SHARD BLOCKCHAIN HASH LIST"].save({"SHARD ID": 1735262821, "BHEIGHT": 102, "BLOCK HASH": "SUPER BLOCK HASH"}))
            print(self.mongo["SHARD BLOCKCHAIN HASH LIST"].save({"SHARD ID": 1735262821, "BHEIGHT": 103, "BLOCK HASH": "SUPER BLOCK HASH"}))
            print(self.mongo["SHARD BLOCKCHAIN HASH LIST"].save({"SHARD ID": 1735262821, "BHEIGHT": 104, "BLOCK HASH": "SUPER BLOCK HASH"}))

            return json.dumps({"STATUS": "OK", "DESCRIPTION": ""}, separators=(',', ':'))

        @self.app.route('/r/registerNewShard', methods=['POST'])
        def regNewShard():
            if not request:
                abort(400)

            jdata = json.loads(request.data)

            shardName = jdata.get('sn')
            shardSign = jdata.get('sg') # sign(shardName) - !!! OR ANOTHER
            shardOwner = jdata.get('ow')
            shardInfo = jdata.get('si')
            shardStemIp = jdata.get('ip')

            if self.mongo["SHARD LIST"].find({"NAME": shardName}).count() != 0:
                return json.dumps({"STATUS": "FAIL", "DESCRIPTION": "SHARD ALREADY EXISTS"}, separators=(',', ':'))

            # check payment for create shard
            # CHECK SIGN CORRECTLY
            print({"NAME": shardName, "OWNER": shardOwner, "INFO": shardInfo, "SIGN": shardSign, "STEMIP": shardStemIp})
            shardId = self.mongo["SHARD LIST"].save({"NAME": shardName, "OWNER": shardOwner, "INFO": shardInfo, "SIGN": shardSign, "STEMIP": shardStemIp})
            return json.dumps({"STATUS": "OK", "DESCRIPTION": str(shardId)}, separators=(',', ':'))

        @self.app.route('/r/addNode', methods=['POST'])
        def addNodeToShard():
            if not request:
                abort(400)

            jdata = json.loads(request.data)

            nodeName = jdata.get('nn')
            shardId = jdata.get('si')
            nodeIp = jdata.get('ni')
            nodePuk = jdata.get('puk')
            nodeType = jdata.get('nt')

            #CHECK NODE APP BEFORE ADDING IN LIST (PING NODE)
            if self.mongo["SHARD LIST"].find({"_id": ObjectId(shardId)}).count() != 1:
                return json.dumps({"STATUS": "FAIL", "DESCRIPTION": "SHARD NO EXIST"}, separators=(',', ':'))

            signature = jdata.pop("sg")
            puk = self.mongo["SHARD LIST"].find_one({"_id": ObjectId(shardId)}).get("OWNER")

            if not self.cryptor.verifyMessage(signature, puk, json.dumps(jdata, separators=(',', ':'))):
                return json.dumps({"STATUS": "FAIL", "DESCRIPTION": "SIGNATURE VERIFY IS FAILED"}, separators=(',', ':'))

            if self.mongo["SHARD NODES LIST"].find({"SHARD ID": shardId, "NODE IP": nodeIp}).count() != 0:
                print(3)
                return json.dumps({"STATUS": "FAIL", "DESCRIPTION": "NODE WITH THIS IP ALREADY EXISTS, YOU HAVE TO DELETE IT BEFORE"}, separators=(',', ':'))
            shardId = self.mongo["SHARD NODES LIST"].save({"NAME": nodeName, "SHARD ID": shardId, "NODE IP": nodeIp, "NODE PKEY": nodePuk, "NODE TYPE": nodeType})
            return json.dumps({"STATUS": "OK", "DESCRIPTION": str(shardId)}, separators=(',', ':'))

        @self.app.route('/r/saveBlockHash', methods=['POST'])
        def saveBlockHash():
            if not request:
                abort(400)

            jdata = json.loads(request.data)

            bheight = jdata.get('bh')
            hash = jdata.get('ha')
            shardId = jdata.get('si')
            signature = jdata.pop('sg')
            if self.mongo["SHARD LIST"].find({"_id": ObjectId(shardId)}).count() == 0:
                return json.dumps({"STATUS": "FAIL", "DESCRIPTION": "SHARD NO EXIST"}, separators=(',', ':'))
            puk = self.mongo["SHARD LIST"].find_one({"_id": ObjectId(shardId)}).get("OWNER")
            if not self.cryptor.verifyMessage(signature, puk, json.dumps(jdata, separators=(',', ':'))):
                return json.dumps({"STATUS": "FAIL", "DESCRIPTION": "SIGNATURE VERIFY IS FAILED"}, separators=(',', ':'))
            blockId = self.mongo["SHARD BLOCKCHAIN HASH LIST"].save({"SHARD ID": shardId, "BHEIGHT": bheight, "BLOCK HASH": hash})
            return json.dumps({"STATUS": "OK", "DESCRIPTION": str(blockId)}, separators=(',', ':'))

        @self.app.route('/r/saveMapElement', methods=['GET','POST'])
        def saveMapElement():
            if not request:
                abort(400)

            name = request.args.get('name')
            nsource = request.args.get('nsource')
            address = request.args.get('address')
            refresh = request.args.get('refresh')
            dtype = request.args.get('dtype')
            costway = request.args.get('costway')
            countway = request.args.get('countway')
            keyway = request.args.get('keyway')

            if costway == "":
                costway = []
            else:
                costway = costway.split(",")

            if countway == "":
                countway = []
            else:
                countway = countway.split(",")

            if keyway == "":
                keyway = []
            else:
                keyway = keyway.split(",")

            data = json.loads(self.redis.get("RATE SOURCES LIST"))["DATA"]
            data.append({"NAME":name, "REFRESH":refresh, "SOURCE_NAME": nsource, "ADDR": address, "DATA_TYPE": dtype, "COST_WAY": costway, "COUNT_WAY": countway, "WAY_TO_KEY_LIST": keyway})
            print(data)
            self.redis.set("RATE SOURCES LIST", json.dumps({"DATA":data}, separators=(',', ':')))

            return json.dumps({"STATUS": "OK"}, separators=(',', ':'))

        @self.app.route('/r/getDataMap', methods=['GET','POST'])
        def getDataMap():
            if not request:
                abort(400)
            data = self.redis.get("RATE SOURCES LIST")
            if data is None:
                data = json.dumps({"DATA":"[]"})
            return data

        @self.app.route('/r/testUserName', methods=['GET','POST'])
        def testUserName():
            if not request:
                abort(400)
            uname = request.args.get('uname')
            data = self.redis.zscore("USER LIST", uname)
            if data is None:
                data = json.dumps({"STATUS": True, "RESULT": True}, separators=(',', ':'))
            else:
                data = json.dumps({"STATUS": True, "RESULT": False}, separators=(',', ':'))
            return data

        @self.app.route('/r/getOsStat', methods=['GET','POST'])
        def getOsStat():
            if not request:
                abort(400)

            cpu = psutil.cpu_percent(interval=0.1)

            memt = psutil.virtual_memory().total / (1024 ** 3)
            memu = psutil.virtual_memory().used / (1024 ** 3)
            memf = psutil.virtual_memory().free / (1024 ** 3)
            memp = psutil.virtual_memory().percent

            swapt = psutil.swap_memory().total / (1024 ** 3)
            swapu = psutil.swap_memory().used / (1024 ** 3)
            swapf = psutil.swap_memory().free / (1024 ** 3)
            swapp = psutil.swap_memory().percent

            data = json.dumps({"CPU": cpu, "MEM":{"TOTAL": round(memt, 2), "USED": round(memu, 2), "FREE": round(memf, 2), "PERCENT": memp}, "SWAP":{"TOTAL": round(swapt, 2), "USED": round(swapu, 2), "FREE": round(swapf, 2), "PERCENT": swapp}}, separators=(',', ':'))
            return data

        @self.app.route('/shardDsgn/createShard', methods=['POST'])
        def createShard():

            if not request:
                abort(400)

            uniqueName = str(uuid.uuid4())
            work_folder = 'shardDesigner/' + uniqueName
            node_folder = 'shardDesigner/' + uniqueName + '/shardNodeDir'
            stem_folder = 'shardDesigner/' + uniqueName + '/shardStemDir'
            binary_folder = 'shardDesigner/' + uniqueName + '/shardNodeDir'
            if not os.path.exists(work_folder):
                shutil.copytree("shardDesigner/shardTemplateDir", work_folder)

            name = request.args.get('name')
            hashType = request.args.get('hash')
            signType = request.args.get('sign')
            freq = request.args.get('freq')
            ipaddr = request.args.get('ipaddr')
            elipad = request.args.get('elipad')
            stempk = request.args.get('stempk')
            command = request.args.get('command')
            fields = request.args.get('fields')
            fieldsMas = "[\"" + fields.replace(",", "\",\"") + "\"]"

            data = ""

            file = request.files['binary']
            binaryName = secure_filename(file.filename)

            file.save(os.path.join(binary_folder, "NODE_BINARY"))

            # !!! CHANGE NODES SCRIPTS !!!

            # 1. CHANGE START NODE SCRIPTS
            command = command.replace(binaryName, "NODE_BINARY")
            print("CHANGE FILE:", "NODE BINARY")

            # 2. CHANGE MRKL SCRIPT
            way = binary_folder + "/crypto/mrkl.py"
            print("CHANGE FILE:", way)
            if os.path.exists(way):
                fnode = open(way, "r")
                internalText = fnode.read()
                fnode.close()

                fnode = open(way, "w")
                internalText = internalText.replace("<%HASH_TYPE%>", hashType)
                fnode.write(internalText)
                fnode.close()
            else:
                data = json.dumps({"STATUS": False, "DESCR": "INTERNAL ERROR, NOT FOUND MRKL SCRIPT"}, separators=(',', ':'))
                return data

            # 3. CHANGE VNCCRYPTO SCRIPT
            way = binary_folder + "/crypto/vncCrypto.py"
            print("CHANGE FILE:", way)
            if os.path.exists(way):
                fnode = open(way, "r")
                internalText = fnode.read()
                fnode.close()

                fnode = open(way, "w")
                internalText = internalText.replace("<%SIGN_TYPE%>", signType)
                fnode.write(internalText)
                fnode.close()
            else:
                data = json.dumps({"STATUS": False, "DESCR": "INTERNAL ERROR, NOT FOUND VNCCRYPTO SCRIPT"}, separators=(',', ':'))
                return data

            # 4. CHANGE SLAVE NODE SCRIPT
            way = binary_folder + "/slaveNode.py"
            print("CHANGE FILE:", way)
            if os.path.exists(way):
                fnode = open(way, "r")
                internalText = fnode.read()
                fnode.close()

                fnode = open(way, "w")
                internalText = internalText.replace("<%FIELDS%>", fieldsMas).replace("<%STEMIP%>", ipaddr).replace("<%STEMPK%>", stempk)
                fnode.write(internalText)
                fnode.close()
            else:
                data = json.dumps({"STATUS": False, "DESCR": "INTERNAL ERROR, NOT FOUND SLAVE NODE SCRIPT"}, separators=(',', ':'))
                return data

            # 5. CHANGE SLAVE NODE SCRIPT
            way = binary_folder + "/static/index.html"
            print("CHANGE FILE:", way)
            if os.path.exists(way):
                fnode = open(way, "r")
                internalText = fnode.read()
                fnode.close()

                fnode = open(way, "w")
                internalText = internalText.replace("<%SHARD NAME%>", name)
                fnode.write(internalText)
                fnode.close()
            else:
                data = json.dumps({"STATUS": False, "DESCR": "INTERNAL ERROR, NOT FOUND INDEX PAGE"}, separators=(',', ':'))
                return data

            # 6. CHANGE SLAVE NODE SCRIPT
            way = binary_folder + "/starterFlask.py"
            print("CHANGE FILE:", way)
            if os.path.exists(way):
                fnode = open(way, "r")
                internalText = fnode.read()
                fnode.close()

                fnode = open(way, "w")
                internalText = internalText.replace("<%START BINARY COMMAND%>", command)
                fnode.write(internalText)
                fnode.close()
            else:
                data = json.dumps({"STATUS": False, "DESCR": "INTERNAL ERROR, NOT FOUND INDEX PAGE"}, separators=(',', ':'))
                return data

            # !!! CHANGE STEM SCRIPTS !!!

            # 5. CHANGE STEM NODE SCRIPT
            way = stem_folder + "/static/index.html"
            print("CHANGE FILE:", way)
            if os.path.exists(way):
                fnode = open(way, "r")
                internalText = fnode.read()
                fnode.close()

                fnode = open(way, "w")
                internalText = internalText.replace("<%SHARD NAME%>", name + "(STEM)")
                fnode.write(internalText)
                fnode.close()
            else:
                data = json.dumps({"STATUS": False, "DESCR": "INTERNAL ERROR, NOT FOUND INDEX PAGE"}, separators=(',', ':'))
                return data

            # 6. CHANGE STEM NODE SCRIPT ELASTIC
            way = stem_folder + "/log/elast.py"
            print("CHANGE FILE:", way)
            if os.path.exists(way):
                fnode = open(way, "r")
                internalText = fnode.read()
                fnode.close()

                fnode = open(way, "w")
                internalText = internalText.replace("<%ELASTICIP%>", elipad)
                fnode.write(internalText)
                fnode.close()
            else:
                data = json.dumps({"STATUS": False, "DESCR": "INTERNAL ERROR, NOT FOUND INDEX PAGE"}, separators=(',', ':'))
                return data

            # PY COMPILE
            #py_compile.compile(node_folder + "/slaveNode.py", cfile=node_folder + "/nodeApp.pyx")
            #py_compile.compile(node_folder + "/starterFlask.py", cfile=node_folder + "/starterApp.pyx")


            print("START ZIP!")

            # ZIP AND SEND FILES!
            zipfNode = zipfile.ZipFile(work_folder + '/nodeApp.zip', 'w', zipfile.ZIP_DEFLATED)
            FlaskWorker.zipDir(node_folder, zipfNode)
            zipfNode.close()
            print("NEXT ZIP!")
            zipfStem = zipfile.ZipFile(work_folder + '/stemApp.zip', 'w', zipfile.ZIP_DEFLATED)
            FlaskWorker.zipDir(node_folder, zipfStem)
            zipfStem.close()
            # ZIP AND SEND FILES!
            print("END ZIP!")

            # REGISTRY NEW SHARD IN ROOT MONGO DATABASE
            print("REGISTRY NEW SHARD IN ROOT MONGO DATABASE")
            shardId = self.mongo["SHARD LIST"].save({"NAME": name, "OWNER": stempk, "INFO": "", "SIGN": "", "STEMIP": ipaddr})
            # REGISTRY NEW SHARD IN ROOT MONGO DATABASE

            data = json.dumps({"STATUS": True, "RESULT": uniqueName, "SHARDID": shardId}, separators=(',', ':'))

            return data

        @self.app.route('/r/newUser', methods=['GET','POST'])
        def newUser():
            if not request:
                abort(400)
            fname = request.args.get('fname')
            lname = request.args.get('lname')
            uname = request.args.get('uname')
            email = request.args.get('email')
            address = request.args.get('address')
            address2 = request.args.get('address2')

            if fname == "":
                data = json.dumps({"STATUS": True, "RESULT": "FNAME not valid"}, separators=(',', ':'))
                return data

            if lname == "":
                data = json.dumps({"STATUS": True, "RESULT": "LNAME not valid"}, separators=(',', ':'))
                return data

            if uname == "":
                data = json.dumps({"STATUS": True, "RESULT": "UNAME not valid"}, separators=(',', ':'))
                return data

            if email == "":
                data = json.dumps({"STATUS": True, "RESULT": "EMAIL not valid"}, separators=(',', ':'))
                return data

            if address == "":
                data = json.dumps({"STATUS": True, "RESULT": "ADDRESS not valid"}, separators=(',', ':'))
                return data

            list = self.redis.get("USER:" + uname)

            if len(list) == 0:
                data = self.redis.zadd("USER:" + uname, json.dumps({"fname": fname, "lname": lname, "uname": uname, "email": email, "address": address,  "address2": address2}, separators=(',', ':')))
            else:
                data = json.dumps({"STATUS": True, "RESULT": "UNAME is USED"}, separators=(',', ':'))
                return data

            if data is None:
                data = json.dumps({"STATUS": True, "RESULT": True}, separators=(',', ':'))
            else:
                data = json.dumps({"STATUS": True, "RESULT": False}, separators=(',', ':'))
            return data


        @self.app.route('/getNodeAppZip')
        def send_nodeAppZip():
            uuid = request.args.get('uuid')
            return send_from_directory("shardDesigner/" + uuid, "nodeApp.zip")

        @self.app.route('/getStemAppZip')
        def send_stemAppZip():
            uuid = request.args.get('uuid')
            return send_from_directory("shardDesigner/" + uuid, "stemApp.zip")



    @staticmethod
    def zipDir(path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    def run(self):
        self.app.run(host='0.0.0.0', port=5005)


if __name__ == '__main__':

    flask = FlaskWorker()
    flask.run()
