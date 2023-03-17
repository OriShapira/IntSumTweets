from shutil import copyfile
import os
import logging

USERS_FILE = 'db/users.txt'
USERSTUDIES_FILE = 'db/userStudies.txt'
INIT_JSON_FILENAME = 'db/init.json'
MAIN_FOLDER = 'db/jsonsMains'
QUESTIONS_FOLDER = 'db/jsonsQuestions'
BASELINES_FOLDER = 'db/jsonsBaselines'
BASELINES2_FOLDER = 'db/jsonsBaselines2'

# possible steps
BASELINE = 4
MAIN = 5
QUESTIONS = 6
BASELINE_QUESTIONS = 7
MAIN_QUESTIONS = 8
BASELINE2 = 9
BASELINE2_QUESTIONS = 10

DB_LINE_SEP = ';;;' # separations between parameters on lines of database files

def resetTestUser(username='tstusr'):
    try:
        logging.info('Resetting ' + username)
        
        # reset registration info:
        setUserRegistrationInfo(username,'','','','')
        
        # go over all the user studies and mark them as not done:
        stepsDS = getUserStudiesDataStructure(username)
        if stepsDS != None:
            for idx, stepsDict in enumerate(stepsDS):
                stepsDict['done'] = False
                
        # write it to the database:
        writeStepsDSforUser(username, stepsDS, 'resetTestUser')
    except:
        logging.error('Error while resetting ' + username)

def setUserRegistrationInfo(username, age, gender, education, occupation):
    logging.info('Registering user ' + username + ' with info: ' + str(age) + ' ' + gender + ' ' + education + ' ' + occupation)
    rewriteFile(USERS_FILE, 'setUserRegistrationInfo', lineLogicUserRegistrationInfo, username, age, gender, education, occupation)
    
def lineLogicUserRegistrationInfo(line, username, age, gender, education, occupation):
    retLine = ''
    splitLine = line.split(DB_LINE_SEP)
    u = splitLine[0]
    p = splitLine[1]
    # when the line with the user name is found, replace it with a line with all the reg info:
    if u == username:
        # for the test user, enable resetting by sending all empty values:
        if username == 'tstusr' and age == '' and gender == '' and education == '' and occupation == '':
            retLine = u + DB_LINE_SEP + p + DB_LINE_SEP + 'null'
        else:
            retLine = u + DB_LINE_SEP + p + DB_LINE_SEP + str(age) + ',' + gender + ',' + education + ',' + occupation
    else:
        retLine = line
    return retLine
    
def setUserStudyResults(username, userStudyIdx, userStudyResults):
    logging.info('Setting user study results for user ' + username + ' for index ' + str(userStudyIdx) + ': ' + str(userStudyResults))
    
    stepsDS = getUserStudiesDataStructure(username)
    
    try:
        stepsDS[userStudyIdx]['done'] = True
        stepsDS[userStudyIdx]['results'] = []
        for stepDict in userStudyResults:
            stepsDS[userStudyIdx]['results'].append(stepDict)
        
        writeStepsDSforUser(username, stepsDS, 'setUserStudyResults')
    except Exception as e:
        logging.error('Error while setting user study results: ' + str(e))

def writeStepsDSforUser(username, stepsDS, callerName):
    logging.info('Writing dataset to db for user ' + username)
    
    stepsDS_str = createUserStudiesDSstring(stepsDS)
    rewriteFile(USERSTUDIES_FILE, callerName, lineLogicWriteStepsDS, username, stepsDS_str)
    
def lineLogicWriteStepsDS(line, username, stepsDS_str):
    retLine = ''
    
    splitLine = line.split(DB_LINE_SEP)
    u = splitLine[0]
    if len(splitLine) > 2:
        feedback = splitLine[2]
    else:
        feedback = None
    # when the line with the user name is found, replace it with a line with the updated data structure:
    if u == username:
        retLine = u + DB_LINE_SEP + stepsDS_str
        if feedback != None:
            retLine += (DB_LINE_SEP + feedback)
    else:
        retLine = line
    return retLine
    
def setUserFeedback(username, userStudyIdx, feedback):
    logging.info('Setting user study feedback for user ' + username + ' for index ' + str(userStudyIdx) + ': ' + feedback)
    rewriteFile(USERSTUDIES_FILE, 'setUserFeedback', lineLogicUserFeedback, username, feedback)

def lineLogicUserFeedback(line, username, feedback):
    # TODO: Bug potential - if an answer or feedback has a semicolon, the line could be split on it
    
    retLine = ''
    splitLine = line.strip().split(DB_LINE_SEP)
    u = splitLine[0]
    # when the line with the username is found, replace it with a line with the feedback:
    if u == username:
        if len(splitLine) <= 2: # there's no feedback yet
            retLine = line.strip() + DB_LINE_SEP + feedback
        else:
            retLine = line.strip() + ' ;; ' + feedback # concatenate new feedback to the end
    else:
        retLine = line
    return retLine
        
def rewriteFile(filepath, callerName, lineLogicFunc, *args):
    # make a backup of the file in case the rewrite fails:
    try:
        backupPath = filepath+'.bkp'
        copyfile(filepath, backupPath)
    except Exception as e:
        logging.error('Failed to make a backup copy of "' + filepath + '" to "' + backupPath + '" for operation ' + callerName)
    
    try:
        with open(filepath, 'r') as fIn:
            allLines = fIn.readlines()
        for i in range(len(allLines)):
            lineToWrite = lineLogicFunc(allLines[i].strip(), *args)
            lineToWrite.replace('\n', ' ').replace('\r', ' ') # remove any newlines possibly place in the text
            allLines[i] = lineToWrite + '\n'
        with open(filepath, 'w') as fOut:
            for line in allLines:
                fOut.write(line)
    except Exception as e:
        logging.error('Error while rewriting file ' + filepath + ' from ' + callerName + ': ' + str(e))

def createUserStudiesDSstring(stepsDS):
    dsStr = str(stepsDS)
    dsStr = dsStr.replace('(4,','(BASELINE,')
    dsStr = dsStr.replace('(5,','(MAIN,')
    dsStr = dsStr.replace('(6,','(QUESTIONS,')
    dsStr = dsStr.replace('(7,','(BASELINE_QUESTIONS,')
    dsStr = dsStr.replace('(8,','(MAIN_QUESTIONS,')
    dsStr = dsStr.replace('(9,','(BASELINE2,')
    dsStr = dsStr.replace('(10,','(BASELINE2_QUESTIONS,')
    return dsStr


def getIsUserAuthorized(username, password):
    userAuthorized = False
    needToRegister = False
    with open(USERS_FILE, 'r') as fIn:
        for line in fIn:
            splitLine = line.strip().split(DB_LINE_SEP)
            u = splitLine[0]
            p = splitLine[1]
            r = splitLine[2]
            if u == username and p == password:
                userAuthorized = True
                if r == 'null':
                    needToRegister = True
                break
                
    return userAuthorized, needToRegister

def getUserStudiesDataStructure(username):
    # get the datastructure from the database file:
    stepsDS = None
    
    try:
        with open(USERSTUDIES_FILE, 'r') as fIn:
            for line in fIn:
                splitLine = line.strip().split(DB_LINE_SEP)
                u = splitLine[0]
                stepsDS_str = splitLine[1]
                if u == username:
                    exec("stepsDS = %s" % stepsDS_str) # convert the string to the python data structure
                    break
    except Exception as e:
        logging.error('Error in getUserStudiesDataStructure: ' + str(e))
    
    # The datastructure looks like: [ {'done':[True|False],'story':<story name>,'steps':<List of pairs (stepEnum,allowedTime) BASELINE|MAIN|QUESTIONS|BASELINE_QUESTION|MAIN_QUESTIONS>} ]
    return stepsDS
    
def getNextUserStudyForUser(username):
    '''
    Get the next user study for the user that was not done yet.
    '''
    stepsDS = getUserStudiesDataStructure(username)
    
    # get the next user study that was not done yet (if all were done, <None,'',-1> will be returned):
    nextUserStudyIndex = -1
    nextStepsList = None
    nextStoryName = ''
    if stepsDS != None:
        for idx, stepsDict in enumerate(stepsDS):
            if stepsDict['done'] == False:
                nextUserStudyIndex = idx
                nextStepsList = stepsDict['steps']
                nextStoryName = stepsDict['story']
                break
    
    return nextStepsList, nextStoryName, nextUserStudyIndex
    
def getNumUserStudies(username):
    stepsDS = getUserStudiesDataStructure(username)
    numDone = 0
    numTotal = 0
    if stepsDS != None:
        numTotal = len(stepsDS)
        for stepsDict in stepsDS:
            if stepsDict['done'] == True:
                numDone += 1
    return numDone, numTotal


def getJsonFromFile(filepath, storyName, jsonType):
    jsonTxt = ''
    try:
        with open(filepath, 'r') as fIn:
            jsonTxt = fIn.read()
    except:
        jsonTxt = getErrorJson('Could not find ' + jsonType + ' JSON for ' + storyName)
    return jsonTxt

def getInitJson():
    return getJsonFromFile(INIT_JSON_FILENAME, '', 'init')
    
def getBaselineJson(storyName):
    return getJsonFromFile(BASELINES_FOLDER+'/'+storyName+'.json', storyName, 'baseline')
    
def getQuestionsJson(storyName):
    return getJsonFromFile(QUESTIONS_FOLDER+'/'+storyName+'.json', storyName, 'questions')
    
def getMainJson(storyName):
    return getJsonFromFile(MAIN_FOLDER+'/'+storyName+'.json', storyName, 'main')
    
def getBaseline2Json(storyName):
    return getJsonFromFile(BASELINES2_FOLDER+'/'+storyName+'.json', storyName, 'baseline2')

def getErrorJson(stopReasonStr):
    jsonReply = "{\"error\": \"" + stopReasonStr + "\" }"
    logging.info("Sending Error JSON.")
    return jsonReply