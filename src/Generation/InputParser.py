import json

# the input formats:
INPUT_FORMAT_OLD = 1
INPUT_FORMAT_NEW = 2

# states of parsing the input:
TITLE = 0
PROP_DICT = 1
ENTS = 2
PROPS = 3
PREDS = 4
ARGS = 5

# to keep track for the predicates and arguments state, keep the current proposition:
m_curProposition = -1
m_curEntityId = 0

def parseInput(inputFormat, okrDataFilePath, okrData, tweetsListFilePath=None, tweetsMetadataFilePath=None):
    if inputFormat == INPUT_FORMAT_OLD:
        parseTweetsFiles(tweetsListFilePath, tweetsMetadataFilePath, okrData)
        parseOkrDataOld(okrDataFilePath, okrData)
    elif inputFormat == INPUT_FORMAT_NEW:
        parseOkrDataNew(okrDataFilePath, okrData)

def parseOkrDataNew(okrDataFilePath, okrData):
    jsonObj = None
    with open(okrDataFilePath, 'r') as inF:
        try:
            jsonObj = json.load(inF)
        except:
            print 'Error: Bad input JSON.'

    if jsonObj != None:
        # get the tweets info:
        for tweetId, tweetInfo in jsonObj['tweets'].iteritems():
            okrData.addTweet(long(tweetId), tweetInfo['string'])
            okrData.updateTweetMetadata(long(tweetId), tweetInfo['timestamp'], tweetInfo['author'], None)

        # get the entities info:
        for entityId, entityInfo in jsonObj['entities'].iteritems():
            okrData.addEntity(entityId, entityInfo['alias'])
            for mentionInfo in entityInfo['mentions']:
                okrData.addEntityMention(entityId, mentionInfo['term'], len(mentionInfo['sources']))

        # get the propositions info:
        for propId, propInfo in jsonObj['propositions'].iteritems():
            okrData.addProposition(propId, propInfo['alias'])
            okrData.setPropositionProperties(propId, None, propInfo['attribution'])
            # templates:
            for templateInfo in propInfo['predicates']['templates']:
                okrData.addPropositionTemplate(propId, templateInfo['template'], map(long, templateInfo['sources']))
            # arguments:
            idsUsed = {} # for a bug where arguments are listed more than once
            for argInfo in propInfo['arguments']:
                if argInfo['id'].startswith('a.'): # in old versions, the arugment ID was <a.1> not it's just <1>
                    argId = int(argInfo['id'][2:])
                else:
                    argId = int(argInfo['id'])
                if not argId in idsUsed:
                    okrData.addPropositionArgument(propId, argId, argInfo['label'])
                    for argMentionInfo in argInfo['values']:
                        okrData.addPropositionArgumentMention(propId, argId, argMentionInfo['concept-id'], map(long, argMentionInfo['sources']))
                    idsUsed[argId] = 1

    okrData.prepareData()

def parseOkrDataOld(okrDataFilePath, okrData):
    cur_parse_state = TITLE

    with open(okrDataFilePath, 'r') as inF:
        for line in inF:
            line = line.strip()
            if line.startswith('#'):
                if line.startswith('#proposition-dict'):
                    cur_parse_state = PROP_DICT
                    continue
                elif line.startswith('#entities'):
                    cur_parse_state = ENTS
                    continue
                elif line.startswith('#proposition'):
                    cur_parse_state = PROPS
                    # don't continue since the info is on the same line
                elif line.startswith('#predicates'):
                    cur_parse_state = PREDS
                    continue
                elif line.startswith('#arguments'):
                    cur_parse_state = ARGS
                    continue

            if line != '':
                handleLine(cur_parse_state, line, okrData)

    okrData.prepareData()

def handleLine(parseState, line, okrData):
    if parseState == PROP_DICT:
        handleLinePropDict(line, okrData)
    elif parseState == ENTS:
        handleLineEntity(line, okrData)
    elif parseState == PROPS:
        handleLineProposition(line, okrData)
    elif parseState == PREDS:
        handleLinePredicate(line, okrData)
    elif parseState == ARGS:
        handleLineArgument(line, okrData)


def handleLinePropDict(line, okrData):
    # example: 9	Condemn (blast - Jonathan)	condemn	condemns	has condemned as	has condemned as	condemns
    lineParts = line.split('\t')
    propId = 'P' + lineParts[0].strip()
    propAlias = lineParts[1].strip()
    #propMentions = list(set(lineParts[2:]))  # remove redundancies of mention terms
    #m_propositions[propId] = {'alias': propAlias, 'mentions': propMentions, 'templates': [], 'args': {},
    #                          'predicateWords': {}}

    okrData.addProposition(propId, propAlias)


def handleLineEntity(line, okrData):
    global m_curEntityId
    # example: bomber	himself[1]	suicidebomber[1]	sole bomber[1]	self[1]	bombers[1]	bomber[19]; sole bomber->bombers	suicidebomber->sole bomber	sole bomber->bomber	suicidebomber->bomber	suicidebomber->bombers	bomber=bombers

    details, entailment = line.split(';')
    lineParts = details.split('\t')
    entAlias = lineParts[0]
    entMentions = {} # TODO: Will need to keep the tweetIDs for each mention instead of just the count
    for linePart in lineParts[1:]:
        term, count = linePart.split('[')
        entMentions[term] = int(count[:-1])
    entId = 'E' + str(m_curEntityId)
    m_curEntityId += 1

    okrData.addEntity(entId, entAlias)
    for mention, mentionCount in entMentions.iteritems():
        okrData.addEntityMention(entId, mention, mentionCount)


def handleLineProposition(line, okrData):
    global m_curProposition

    # example: #proposition P0	2012-10-28 08:11:10
    lineParts = line.split()
    propId = lineParts[1]
    propDate = lineParts[2]
    propTime = lineParts[3]
    if len(lineParts) > 4:
        propAttribution = lineParts[4].split(':')[1].strip()  # example: "Attributor: BBC News"
    else:
        propAttribution = None
    m_curProposition = propId

    okrData.setPropositionProperties(propId, propDate + ' ' + propTime, propAttribution)


def handleLinePredicate(line, okrData):
    # example: <a.1.2> , <a.1.1>[1,262795593573859328]	<a.1.2> in <a.1.1>[18,262524557754261504,262498758795866113,262502692755234816,262528827656372226,262528722635206656,262495180949700608,262468815630262274,262503531578261505,262494539284107264,262568799205736448,262617948034834432,262567327185379329,262630594108878850,262573345734799362,262487152942788608,262479779209551872,262492848685985792,262525686059769856]	IMPLICIT[31,262485395445514240,262580165765373955,262555583113228288,262506182562959360,262603197007421442,262690371123961856,262844952386609152,262678652477644801,262605163989180416,262557898218024960,262601334635786242,262836211486449664,262479280469049344,262959695743053824,262557030177468416,262604706961035265,262534116547907584,262816078865002496,262492852901269504,262501652622344192,263019158613135360,262527552642482176,262516169263681537,262836601409921024,262656078624477184,262513929241104384,262578660027006977,262530714921234433,262919166380621824,262511756675534849,262492915786477568];

    lineParts = line.split('\t')
    for predInfo in lineParts:
        predTemplate, tweetsListStr = predInfo.split('[')

        # get the integer list of tweet ids
        tweetsList = map(int, tweetsListStr.strip(';')[:-1].split(',')[
                              1:])  # the first item in the list is the number of tweets -- ignore it

        okrData.addPropositionTemplate(m_curProposition, predTemplate, tweetsList)


def handleLineArgument(line, okrData):
    # example: a.1.1	where is something?	Kaduna[50,262485395445514240,262580165765373955,262555583113228288,262506182562959360,262603197007421442,262690371123961856,262844952386609152,262678652477644801,262605163989180416,262557898218024960,262601334635786242,262836211486449664,262524557754261504,262498758795866113,262502692755234816,262528827656372226,262528722635206656,262495180949700608,262468815630262274,262503531578261505,262494539284107264,262568799205736448,262617948034834432,262479280469049344,262959695743053824,262557030177468416,262604706961035265,262567327185379329,262534116547907584,262816078865002496,262630594108878850,262573345734799362,262492852901269504,262795593573859328,262487152942788608,262501652622344192,263019158613135360,262527552642482176,262516169263681537,262479779209551872,262836601409921024,262656078624477184,262513929241104384,262578660027006977,262530714921234433,262919166380621824,262511756675534849,262492848685985792,262492915786477568,262525686059769856]

    lineParts = line.split('\t')
    argId = int(lineParts[0].split('.')[-1])  # take the number at the end of the full argID (ex. a.12.3 -> 3)
    argQuestion = lineParts[1]
    okrData.addPropositionArgument(m_curProposition, argId, argQuestion)

    for argMention in lineParts[2:]:
        argRep, tweetsListStr = argMention.split('[')

        tweetsList = map(int,
                         tweetsListStr[:-1].split(',')[1:])  # the first item in the list is the number of tweets -- ignore it

        conceptId = getConceptIdFromArgRepresentative(argRep, okrData)
        okrData.addPropositionArgumentMention(m_curProposition, argId, conceptId, tweetsList)

def getConceptIdFromArgRepresentative(argRep, okrData):
    if argRep.startswith('*P'):
        return argRep[1:]
    else:
        return okrData.getEntityIdFromAlias(argRep)


def parseTweetsFiles(tweetsListFilePath, metadataFilePath, okrData):
    # extract the tweet ID and text from the partial list file:
    tweetsToUpdate = {}
    with open(tweetsListFilePath, 'r') as inF:
        for line in inF:
            if line != '':
                try:
                    tweetId, tweetText = line.strip().split('\t')
                    okrData.addTweet(long(tweetId), tweetText.strip())
                    tweetsToUpdate[tweetId] = 1
                except:
                    continue

    # extract the metadata only of the tweets in the above list:
    with open(metadataFilePath, 'r') as inF:
        for line in inF:
            if line != '':
                tweetId, authorName, authorId, timestamp = line.split('\t')
                if tweetId in tweetsToUpdate:
                    okrData.updateTweetMetadata(long(tweetId), timestamp.strip(), authorName, authorId)