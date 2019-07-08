import os

class NetSettings:
    nodeDataPort = 3333
    nodeCommandPort = 3344
    keysList = ['0323f264fd64a684db1e36a2c97b58867e0625f797008206216576fea2114bdbca']
    purifierList = [os.getenv("SLAVE_PORT_5000_TCP_ADDR")] or ['10.0.3.7']
    purifierPuksList = ['puk']
    def __init__(self):
        return


