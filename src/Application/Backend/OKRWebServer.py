import json
import tornado.httpserver
import tornado.ioloop
import tornado.web
import dbUtils
import logging
import traceback
import datetime


# states:
INIT = 0
SIGNIN = 1
REGISTRATION = 2
FINAL = 9
OTHER_SCREEN = 3
ERROR = 10

# possible stop reasons:
DONTSTOP = 0
FINISHED_USERSTUDY_NOW = 1
ERROR_BADINPUT = 2

## variables for a session (reinitialized when a new session is called):
#m_clientId = None
#m_username = None
#m_userHasRegistered = False
#m_steps = None # the steps of the user study going on now
#m_storyName = None # the name of the story of the user study going on now
#m_userStudyIdx = -1 # just for when saving results to the database
#m_currentStepNum = 0 # the current step in the user study going on now
#m_userStudyResults = [] # for each step, keep the results: [ { 'timeSpent':<int> , 'answers':{qId:answer} } ]

m_clientsInfo = {}

class OKRHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        #self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
    
    def options(self):
        # no body
        logging.debug('Received OPTIONS request')
        self.set_status(204)
    
    def post(self):
        global m_clientsInfo
    
        # Protocol implemented here based on the client messages.
    
        try:
            # load the json received from the client:
            clientJson = json.loads(self.request.body.decode('utf-8'))
            logging.debug('Got JSON data: ' + str(clientJson))
            receivedStepType = self.getStepTypeFromClientJson(clientJson)
            
            # if client sent an unknown json:
            if receivedStepType == ERROR:
                returnJson = dbUtils.getErrorJson('Undefined JSON received.')
            # otherwise there's something to do:
            else:
                # Initialization step:
                if receivedStepType == INIT:
                    # handle new client info and send init info:
                    returnJson, newClientId = self.initialStep(clientJson)
                    # initialize session:
                    if newClientId in m_clientsInfo:
                        del m_clientsInfo[newClientId]
                    m_clientsInfo[newClientId] = { \
                        'username':None, \
                        'userHasRegistered':False, \
                        'steps':None, \
                        'storyName':None, \
                        'userStudyIdx':-1, \
                        'currentStepNum':0, \
                        'userStudyResults':[], \
                        'endTime':None, \
                        'isEvaluation':False \
                    }
                else:
                    # get the clientid sent from the client:
                    curClientId = self.isValidClientId(clientJson)
                    # if this is an unknown clientid, send an error:
                    if curClientId == None:
                        returnJson = dbUtils.getErrorJson('Unrecognized client.')
                    else:
                        ## if no client initialized yet, there is a problem:
                        #if m_clientId == None:
                        #    returnJson = dbUtils.getErrorJson('Initialization was not yet performed.')
                    
                        # SignIn step:
                        #elif receivedStepType == SIGNIN:
                        if receivedStepType == SIGNIN:
                            # handle sign in credentials:
                            returnJson, userAuthorized, username, needToRegister, isEvaluation = self.signInStep(clientJson)
                            m_clientsInfo[curClientId]['username'] = username
                            m_clientsInfo[curClientId]['userHasRegistered'] = not needToRegister
                            m_clientsInfo[curClientId]['isEvaluation'] = isEvaluation
                            if not needToRegister:
                                # the session will start from now:
                                self.initNextUserStudyForUser(curClientId, m_clientsInfo[curClientId]['username'])
                        
                        # not the Initialization or SignIn steps:
                        else:
                            # if no user has signed in yet, do not allow continuing:
                            if m_clientsInfo[curClientId]['username'] == None:
                                returnJson = dbUtils.getErrorJson('No user is signed in.')
                        
                            # The Initialization and SignIn steps have been completed:
                            else:
                                # if the user has not yet registered, do not allow to continue:
                                if receivedStepType != REGISTRATION and not m_clientsInfo[curClientId]['userHasRegistered']:
                                    returnJson = dbUtils.getErrorJson('User has not registered.')
                                
                                # Registration and user study steps:
                                else:
                                    # Registration step:
                                    if receivedStepType == REGISTRATION:
                                        # handles the registration input from the client:
                                        agreementAccepted = self.registrationStep(clientJson, curClientId)
                                        if not agreementAccepted:
                                            returnJson = dbUtils.getErrorJson('User has not registered.')
                                        else:
                                            clientJson = None # prepare for the next screenStep (to send the first screen step)
                                            # the session will start from now:
                                            self.initNextUserStudyForUser(curClientId, m_clientsInfo[curClientId]['username'])
                                
                                    if m_clientsInfo[curClientId]['userHasRegistered']:
                                        # handle the client input on the last screen, and send the next step according to currentStepNum:
                                        returnJson, didUserFinishNow = self.screenStep(clientJson, curClientId);
                                        
                                        m_clientsInfo[curClientId]['currentStepNum'] += 1
                                    
        except Exception as e:
            logging.error('Caught error from unknown location: ' + str(e))
            logging.error(traceback.format_exc())
            returnJson = dbUtils.getErrorJson('Please try again. General error.')
                                
        
        self.write(returnJson) # send JSON to client
            
    def initNextUserStudyForUser(self, curClientId, username):
        global m_clientsInfo
        steps, storyName, userStudyIdx = dbUtils.getNextUserStudyForUser(username)
        m_clientsInfo[curClientId]['steps'] = steps
        m_clientsInfo[curClientId]['storyName'] = storyName
        m_clientsInfo[curClientId]['userStudyIdx'] = userStudyIdx
        m_clientsInfo[curClientId]['currentStepNum'] = 0
        m_clientsInfo[curClientId]['userStudyResults'] = []
        
    def getStepTypeFromClientJson(self, clientJson):
        if 'clientId' in clientJson and len(clientJson) == 1:
            return INIT
        if 'signInScreenOutput' in clientJson:
            return SIGNIN
        elif 'registrationScreenOutput' in clientJson:
            return REGISTRATION
        elif 'currentScreenOutput' in clientJson:
            if 'screenObj1' in clientJson['currentScreenOutput'] and \
                'finishScreenOutput' in clientJson['currentScreenOutput']['screenObj1']:
                return FINAL
            else:
                return OTHER_SCREEN
        else:
            return ''
    
    def isValidClientId(self, jsonMsg):
        if 'clientId' in jsonMsg:
            clientIdSent = jsonMsg['clientId']
            if clientIdSent in m_clientsInfo:
                return clientIdSent
        return None
    
    def initialStep(self, jsonMsg):
        try:
            clientId = jsonMsg['clientId']
            logging.info('Initialize: client ' + clientId)
        except:
            return dbUtils.getErrorJson('Bad JSON received from client. Expected Init.')

        return dbUtils.getInitJson(), clientId
    
    def signInStep(self, jsonMsg):
        try:
            username = jsonMsg['signInScreenOutput']['user']
            password = jsonMsg['signInScreenOutput']['password']
            logging.info('SignIn: Received ' + username + '/****')
        except:
            return dbUtils.getErrorJson("Bad JSON received from client. Expected SignIn.")

        # with the resseting password of the test user, reset its data:
        if username == 'tstusr' and password == 'reset':
            logging.info('Resetting tstusr.')
            dbUtils.resetTestUser(username='tstusr')
            
        userAuthorized, needToRegister = dbUtils.getIsUserAuthorized(username, password)
        isEvaluation = True
        if userAuthorized:
        
            # the demo user does not need to register, and should be reset:
            if username.startswith('demo'):
                dbUtils.resetTestUser(username=username)
                needToRegister = False
                if username != 'demoEval':
                    isEvaluation = False
        
            logging.info("\tAuthorizing!")
            jsonReply = \
                    "{\"signInScreenAuthorization\": {" + \
                    "  \"authorized\": true," + \
                    "  \"registrationScreenInput\": {" + \
                    "    \"message\": \"Welcome to the OKR user study!\","
            if needToRegister:
                jsonReply += \
                    "    \"needRegistration\": true"
            else:
                jsonReply += \
                    "    \"needRegistration\": false"
            jsonReply += \
                    "  }" + \
                    "}}"
        else:
            logging.info("\tNot Authorizing!")
            jsonReply = \
                    "{\"signInScreenAuthorization\": {" + \
                    "  \"authorized\": false" + \
                    "}}"

        return jsonReply, userAuthorized, username, needToRegister, isEvaluation
    
    def registrationStep(self, jsonMsg, curClientId):
        global m_clientsInfo
        
        logging.info("Registration")
        if 'userInfo' in jsonMsg['registrationScreenOutput']:
            agreementAccepted = jsonMsg['registrationScreenOutput']['userInfo']['agreementAccepted']
            age = jsonMsg['registrationScreenOutput']['userInfo']["age"]
            gender = jsonMsg['registrationScreenOutput']['userInfo']["gender"]
            education = jsonMsg['registrationScreenOutput']['userInfo']["education"]
            occupation = jsonMsg['registrationScreenOutput']['userInfo']["occupation"]
            logging.info("\tAgreement Accepted: " + str(agreementAccepted))
            dbUtils.setUserRegistrationInfo(m_clientsInfo[curClientId]['username'], age, gender, education, occupation)
            m_clientsInfo[curClientId]['userHasRegistered'] = agreementAccepted
        else:
            logging.warning('Empty registration given.')
            return m_clientsInfo[curClientId]['userHasRegistered'] # if the user has not registered, return False

        return agreementAccepted
    
    def screenStep(self, jsonMsg, curClientId):
        global m_clientsInfo
        
        # if there's nothing to do:
        if m_clientsInfo[curClientId]['userStudyIdx'] == -1:
            sendObj = self.getGoodbyeJson(curClientId)
        
        # first check the JSON sent from the client (if there is one):
        continueSession = DONTSTOP
        if jsonMsg != None:
            if m_clientsInfo[curClientId]['currentStepNum'] >= len(m_clientsInfo[curClientId]['userStudyResults']):
                m_clientsInfo[curClientId]['userStudyResults'].append({})
            continueSession = self.handleWholeClientScreenInput(jsonMsg, curClientId)

        # if the user has reached the end of a user study, set the results and go to the next user study,
        # (unless there is no other user study left to do -- where userStudyIdx == -1
        # from the last initNextUserStudyForUser call):
        if continueSession == FINISHED_USERSTUDY_NOW:
            # get the next user study:
            self.initNextUserStudyForUser(curClientId, m_clientsInfo[curClientId]['username'])
            continueSession = DONTSTOP
            
        # if we need to send an error:
        if continueSession != DONTSTOP: # and continueSession != FINISHED_USERSTUDY_NOW:
            return self.getErrorJsonByCode(continueSession), False
        # if there's no user study left to do:
        elif m_clientsInfo[curClientId]['userStudyIdx'] == -1:
            sendObj = self.getGoodbyeJson(curClientId)
        # if we need to send the 'final' screen:
        elif m_clientsInfo[curClientId]['currentStepNum'] == len(m_clientsInfo[curClientId]['steps']):
            # set the results of the finished user study into the database:
            dbUtils.setUserStudyResults(m_clientsInfo[curClientId]['username'], m_clientsInfo[curClientId]['userStudyIdx'], m_clientsInfo[curClientId]['userStudyResults'])
            obj1 = self.getFinalJson(curClientId)
            sendObj = "{\"currentScreenInput\": { \"screenObj1\":" + obj1 + " }}"
            
        else:
            currentStepNum = m_clientsInfo[curClientId]['currentStepNum']
            currentStep = m_clientsInfo[curClientId]['steps'][currentStepNum][0]
            currentStepAllowedTime = m_clientsInfo[curClientId]['steps'][currentStepNum][1]
        
            if m_clientsInfo[curClientId]['isEvaluation']:
                isEval = 'true'
            else:
                isEval = 'false'
        
            # create the next screen information JSON:
            if currentStep == dbUtils.BASELINE:
                obj1 = dbUtils.getBaselineJson(m_clientsInfo[curClientId]['storyName'])
                sendObj = "{\"currentScreenInput\": { \"timeAllowed\": " + str(currentStepAllowedTime) + ", \"needDirections\": " + isEval + ", \"screenObj1\":" + obj1 + " }}"
            elif currentStep == dbUtils.QUESTIONS:
                obj1 = dbUtils.getQuestionsJson(m_clientsInfo[curClientId]['storyName'])
                sendObj = "{\"currentScreenInput\": { \"timeAllowed\": " + str(currentStepAllowedTime) + ", \"needDirections\": " + isEval + ", \"screenObj1\":" + obj1 + " }}"
            elif currentStep == dbUtils.BASELINE_QUESTIONS:
                obj1 = dbUtils.getBaselineJson(m_clientsInfo[curClientId]['storyName'])
                obj2 = dbUtils.getQuestionsJson(m_clientsInfo[curClientId]['storyName'])
                sendObj = "{\"currentScreenInput\": { \"timeAllowed\": " + str(currentStepAllowedTime) + ", \"needDirections\": " + isEval + ", \"screenObj1\":" + obj1 + ", \"screenObj2\":" + obj2 + " }}"
            elif currentStep == dbUtils.MAIN:
                obj1 = dbUtils.getMainJson(m_clientsInfo[curClientId]['storyName'])
                sendObj = "{\"currentScreenInput\": { \"timeAllowed\": " + str(currentStepAllowedTime) + ", \"needDirections\": " + isEval + ", \"screenObj1\":" + obj1 + " }}"
            elif currentStep == dbUtils.MAIN_QUESTIONS:
                obj1 = dbUtils.getMainJson(m_clientsInfo[curClientId]['storyName'])
                obj2 = dbUtils.getQuestionsJson(m_clientsInfo[curClientId]['storyName'])
                sendObj = "{\"currentScreenInput\": { \"timeAllowed\": " + str(currentStepAllowedTime) + ", \"needDirections\": " + isEval + ", \"screenObj1\":" + obj1 + ", \"screenObj2\":" + obj2 + " }}"
            elif currentStep == dbUtils.BASELINE2:
                obj1 = dbUtils.getBaseline2Json(m_clientsInfo[curClientId]['storyName'])
                sendObj = "{\"currentScreenInput\": { \"timeAllowed\": " + str(currentStepAllowedTime) + ", \"needDirections\": " + isEval + ", \"screenObj1\":" + obj1 + " }}"
            elif currentStep == dbUtils.BASELINE2_QUESTIONS:
                obj1 = dbUtils.getBaseline2Json(m_clientsInfo[curClientId]['storyName'])
                obj2 = dbUtils.getQuestionsJson(m_clientsInfo[curClientId]['storyName'])
                sendObj = "{\"currentScreenInput\": { \"timeAllowed\": " + str(currentStepAllowedTime) + ", \"needDirections\": " + isEval + ", \"screenObj1\":" + obj1 + ", \"screenObj2\":" + obj2 + " }}"
            
            #elif currentStep == FINAL:
            #    m_curUserStudyNum += 1
            #    obj1 = self.getFinalJson(m_curUserStudyNum, m_numUserStudies)
            #    sendObj = "{\"currentScreenInput\": { \"timeAllowed\": " + currentStepAllowedTime + ", \"screenObj1\":" + obj1 + " }}"

        return sendObj, continueSession==FINISHED_USERSTUDY_NOW
    
    def handleWholeClientScreenInput(self, jsonMsg, curClientId):
        global m_clientsInfo
        
        continueSession = DONTSTOP
        if "currentScreenOutput" in jsonMsg and "timeSpentOpen" in jsonMsg["currentScreenOutput"]:
            timeSpent = jsonMsg["currentScreenOutput"]["timeSpentOpen"]
            currentStepNum = m_clientsInfo[curClientId]['currentStepNum']
            m_clientsInfo[curClientId]['userStudyResults'][currentStepNum-1]['timeSpent'] = timeSpent
            if "screenObj1" in jsonMsg["currentScreenOutput"]:
                continueSession = self.handleSingleScreenInput(jsonMsg["currentScreenOutput"]["screenObj1"], curClientId)
            if continueSession == DONTSTOP and "screenObj2" in jsonMsg["currentScreenOutput"]:
                continueSession = self.handleSingleScreenInput(jsonMsg["currentScreenOutput"]["screenObj2"], curClientId)
        else: # wrong input
            continueSession = ERROR_BADINPUT

        return continueSession
    
    def handleSingleScreenInput(self, singleScreenObject, curClientId):
        global m_clientsInfo
        
        retVal = DONTSTOP
        
        if "baselineScreenOutput" in singleScreenObject:
            logging.debug("Got Baseline response JSON from client.")
        elif "baseline2ScreenOutput" in singleScreenObject:
            logging.debug("Got Baseline2 response JSON from client.")
        elif "dynamicStoryScreenOutput" in singleScreenObject:
            logging.debug("Got Main response JSON from client.")
        elif "questionsScreenOutput" in singleScreenObject:
            logging.debug("Got Questions response JSON from client.")
            answersArray = singleScreenObject["questionsScreenOutput"]["answers"]
            currentStepNum = m_clientsInfo[curClientId]['currentStepNum']
            m_clientsInfo[curClientId]['userStudyResults'][currentStepNum-1]['answers'] = {answersArray[i]["id"]:answersArray[i]["text"] for i in range(len(answersArray))}
            #print "\tAnswers:"
            #for i in range(len(answersArray)):
            #    print "\t\t" + str(answersArray[i]["id"]) + ": " + answersArray[i]["text"]
        elif "finishScreenOutput" in singleScreenObject:
            logging.debug("Got Finish response JSON from client.")
            if 'feedback' in singleScreenObject["finishScreenOutput"]:
                feedback = singleScreenObject["finishScreenOutput"]["feedback"]
                dbUtils.setUserFeedback(m_clientsInfo[curClientId]['username'], m_clientsInfo[curClientId]['userStudyIdx'], feedback)
            retVal = FINISHED_USERSTUDY_NOW
        else:
            logging.error("Unknown JSON output object received for screen output.")
            retVal = ERROR_BADINPUT
                
        return retVal
        
    def getFinalJson(self, curClientId):
        try:
            numDone, numTotal = dbUtils.getNumUserStudies(m_clientsInfo[curClientId]['username'])
            jsonReply = \
                    "{\"finishScreenInput\": {" + \
                    "  \"message\": \"Thanks!\"," + \
                    "  \"studyNumFinished\": " + str(numDone) + "," + \
                    "  \"numStudiesTotal\": " + str(numTotal) + \
                    "}}"
            logging.debug("Sending Finish JSON.")
        except:
            jsonReply = dbUtils.getErrorJson("Could not create Finish JSON.")
            
        return jsonReply
        
    def getGoodbyeJson(self, curClientId):
        global m_clientsInfo
        try:
            jsonReply = "{\"currentScreenInput\": {\"goodbye\":\"Have a nice day :)\"}}"
            logging.debug("Sending Goodbye JSON.")
            
            # set the end time of this client if not already done so:
            if m_clientsInfo[curClientId]['endTime'] == None:
                m_clientsInfo[curClientId]['endTime'] = datetime.datetime.now()
            
            # go over all the clients and remove the ones older than 1 hour:
            currentTime = datetime.datetime.now()
            removeClients = []
            for clientId in m_clientsInfo:
                if m_clientsInfo[clientId]['endTime'] != None:
                    timeDiff = currentTime - m_clientsInfo[clientId]['endTime']
                    if timeDiff.seconds > 3600:
                        removeClients.append(clientId)
            for clientId in removeClients:
                logging.info('Removing client from local memory: ' + clientId)
                del m_clientsInfo[clientId]
            
        except:
            jsonReply = dbUtils.getErrorJson("Could not create Goodbye JSON.")
            
        return jsonReply
        
    def getErrorJsonByCode(self, stopReasonCode):
        if stopReasonCode == ERROR_BADINPUT:
            message = "Bad input received from the client."
        else:
            message = "Unknown"
        return dbUtils.getErrorJson(message)
        
        
    

if __name__ == '__main__':
    #logging.basicConfig(filename='okr.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.basicConfig(filename='okr.log', level=logging.DEBUG, format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')
                               
    app = tornado.web.Application([ tornado.web.url(r'/', OKRHandler) ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(1379)
    logging.info('Starting server on port 1379')
    print 'Starting server on port 1379'
    tornado.ioloop.IOLoop.instance().start()