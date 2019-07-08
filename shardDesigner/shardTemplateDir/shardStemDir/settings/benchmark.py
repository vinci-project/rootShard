from crypto.mrkl import VncTree
import uuid, time

class benchmark:
    def __init__(self):
        self.countIterations = 1000 * 1000
        self.powerFactor = 2 # Нода может быть слабее мастер-ноды не более чем в 2 раза
    #--------------------------------------
        self.clearStemResults = []
        self.usingStemResults = []

    def generateStemResult(self):
        startString = str(uuid.uuid4())
        testString = startString
        startTime = time.time()
        for i in range(0, self.countIterations):
            testString = VncTree.hash(testString)

        testTime = time.time() - startTime
        self.clearStemResults.append({"uuid": startString, "result": testString, "stemTime": testTime})

    def benchmarkStart(self, start):
        testString = start
        for i in range(0, self.countIterations):
            testString = VncTree.hash(testString)
        return testString

    def getStemResult(self, pubk:str):
        if len(self.clearStemResults) == 0:
            return None
        else:
            result = self.clearStemResults.pop(0)
        reUUID = result["uuid"]
        result.update({"key":pubk})
        result.update({"startTime":time.time()})
        self.usingStemResults.append(result)
        return reUUID

    def testNodeResult(self, uuid, result, pubk):
        for test in self.usingStemResults:

            if test["uuid"] == uuid and test["result"] == result and test["key"] == pubk and (time.time() - float(test["startTime"])) <= float(test["stemTime"]*self.powerFactor):
                print ("GOOD POWER OF NODES", test)
                self.usingStemResults.remove(test)
                return True
            else:
                print ("BAD POWER OF NODES", test)
                self.usingStemResults.remove(test)
                return False
        return False