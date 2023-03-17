import json

import Utils


def getSummaryOutputStr(okrData, sentenceOrderInfo, sentencesInfo):
    lines = []

    lines.append('-' * 50)
    lines.append('Summary of ' + str(len(okrData.tweets)) + ' Tweets  ->  ' + str(len(sentenceOrderInfo)) + ' generated sentences')
    lines.append('-' * 50)
    for sentInfo in sentenceOrderInfo:
        sentId = sentInfo['sentenceId']
        lines.append(sentencesInfo[sentId]['sentence'])
        lines.append(sentInfo['timestamp'])
        lines.append('Folded' if sentInfo['fold'] else 'Unfolded')
        lines.append('--- Sentence Expansion: ---')
        for conceptId, conceptStr in sentencesInfo[sentId]['sentenceExpansion'].iteritems():
            lines.append('\t' + conceptStr)
        lines.append('--- Concept Expansions: ---')
        conceptExpansions = sentencesInfo[sentId]['conceptExpansions']
        for argId in conceptExpansions:
            lines.append('\t' + str(argId) + ': ' + str(conceptExpansions[argId]))
        lines.append('--- Source Tweets: ---')
        allTweetIds = sentencesInfo[sentId]['tweets']
        lines.append('\tNumber of tweets: ' + str(len(allTweetIds)))
        lines.append('\t' + str(allTweetIds))
        lines.append('-'*50)

    return '\n'.join(lines)


def getFullOutputString(okrData, sentenceOrderInfo, sentencesInfo):
    lines = []

    for sentInfo in sentenceOrderInfo:
        sentId = sentInfo['sentenceId']
        lines.append(str(sentId) + ':\t' + sentencesInfo[sentId]['sentence'])
        lines.append(sentInfo['timestamp'])
        lines.append(str(sentInfo['fold']))
        lines.append('\t\t' + str(sentencesInfo[sentId]['sentenceInfo']))
        for conceptId, conceptStr in sentencesInfo[sentId]['sentenceExpansion'].iteritems():
            lines.append('\t\t\t' + conceptId + ': ' + conceptStr)
        for propId in sentencesInfo[sentId]['clusterPropIds']:
            lines.append('\t' + propId + ': ' + okrData.propositions[propId].getRepresentingTemplateStr()[0])

        conceptExpansions = sentencesInfo[sentId]['conceptExpansions']
        for argId in conceptExpansions:
            lines.append('\t\t\t' + str(argId) + ': ' + str(conceptExpansions[argId]))

        allTweetIds = sentencesInfo[sentId]['tweets']
        lines.append('\tNumber of tweets: ' + str(len(allTweetIds)))
        lines.append('\t' + str(allTweetIds))

    return '\n'.join(lines)


'''
Old Main JSON:
{
    "dynamicStoryScreenInput": {
        "title": "Boy_scouts",
        "entailmentItems": [
            {"type": "entity", "id":0, "name": "Boy Scouts", "desc":"the boy scouts ; the boy scouts of america ; boy scouts of america ; homophobic boy scouts of america ; scout ; "},
            {"type": "entity", "id":1, "name": "Montana", "desc":"mt ; the state ; "},
            {"type": "predicate", "id":4, "name": "confidential/secret", "desc":"secret ; confidential ; "},
            {"type": "predicate", "id":5, "name": "to be released", "desc":"on to be released ; set to be released ; "},
        ],
        "sentences": [
            {
                "id":54,
                "sentence": "secret files files of scout released by court",
                "timestamp": "2012-10-19 22:17:07",
                "scoreSentence":0.012396694214876028,
                "scoreExtraInfo":0,
                "showOnInit":true,
                "tweets":[258685511210786816, 258700812145016833, 258720307454554113],
                "pressableTokens":[
                    {"tokens":[0],"item":{"type":"predicate","id":4}},
                    {"tokens":[4],"item":{"type":"entity","id":0}}
                ]
            },
            {
                "id":54,
                "sentence": "boy scout files released in montana",
                "timestamp": "2012-10-19 22:17:07",
                "scoreSentence":0.012396694214876028,
                "scoreExtraInfo":0,
                "showOnInit":false,
                "tweets":[258795112623116288, 258799755835101184, 258841904278564864, 258845259805650944],
                "pressableTokens":[
                    {"tokens":[0, 1],"item":{"type":"entity","id":0}},
                    {"tokens":[5],"item":{"type":"entity","id":1}},
                    {"tokens":[3, 4],"item":{"type":"predicate","id":5}}
                ]
            }
        ]
    }
}

New Main JSON:
{
    "dynamicStoryScreenInput": {
        "title": "Boy_scouts",
        "sentences": [
            {
                "id":54,
                "sentence": "secret files of scout released by court",
                "timestamp": "2012-10-19 22:17:07",
                "showOnInit":true,
                "tweets":[258685511210786816, 258700812145016833, 258720307454554113],
                "pressableConcepts":[
                    {"tokens":[0], "conceptId":"P4", "expansion":"confidential ; secret"},
                    {"tokens":[3], "conceptId":"E0", "expansion":"the boy scouts ; boy scouts of america ; homophobic boy scouts of america ; scout"},
                    {"tokens":[4, 5], "conceptId":"P5"}
                ],
                "sentenceExpansion":["high court", "last Friday"]
            },
            {
                "id":78,
                "sentence": "boy scout files released in montana",
                "timestamp": "2012-10-19 22:17:07",
                "showOnInit":false,
                "tweets":[258795112623116288, 258799755835101184, 258841904278564864, 258845259805650944],
                "pressableTokens":[
                    {"tokens":[0, 1], "conceptId":"E0", "expansion":"the boy scouts ; boy scouts of america ; homophobic boy scouts of america ; scout"},
                    {"tokens":[5], "conceptId":"E1", "expansion":"Montana ; mt ; the state"},
                    {"tokens":[3, 4], "conceptId":"P5"}
                ],
                "sentenceExpansion":["1000s of files", "on leaders"]
            },
            ...
        ]
        "foldKeywords": [
            {
                "ids" : [78, ...],
                "keywords" : ["montana", ...]
            }
        ]
    }
}
'''

def createOutputJson(okrData, sentenceOrderInfo, sentencesInfo):
    jsonObj = {"dynamicStoryScreenInput": {"title": okrData.name, "numTweets": len(okrData.tweets), "sentences": [], "foldKeywords": []}}

    conceptIdsToUseForConceptExpansions = _getUsefulConceptIds(sentencesInfo)

    for sentInfo in sentenceOrderInfo:
        sentId = sentInfo['sentenceId']

        sentenceDict = {}
        sentenceDict["id"] = sentId
        sentenceDict["sentence"] = sentencesInfo[sentId]['sentence']
        sentenceDict["timestamp"] = sentInfo['timestamp']
        sentenceDict["showOnInit"] = not sentInfo['fold']
        sentenceDict["tweets"] = sentencesInfo[sentId]['tweets']
        sentenceDict["sentenceExpansion"] = Utils.reduceSentenceExpansionList(sentencesInfo[sentId]['sentenceExpansion'].values())
        sentenceDict["pressableTokens"] = []

        # for each concept in the sentence, create a concept expansion if necessary:
        for conExpInfo in sentencesInfo[sentId]['sentenceInfo']:
            # only put an expansion for the concept if it is in the useful concepts list:
            if conExpInfo['conceptId'] in conceptIdsToUseForConceptExpansions:
                conExp = {}
                conExp["tokens"] = conExpInfo['indices']
                conExp["conceptId"] = conExpInfo['conceptId']
                if 'expansion' in conExpInfo and len(conExpInfo['expansion']) > 0:
                    if 'IMPLICIT' in conExpInfo['expansion']:
                        conExpInfo['expansion'].remove('IMPLICIT')
                    if len(conExpInfo['expansion']) > 0:
                        conExp["expansion"] = ' ; '.join(conExpInfo['expansion'])
                sentenceDict["pressableTokens"].append(conExp)

        jsonObj["dynamicStoryScreenInput"]["sentences"].append(sentenceDict)

    foldedGroupsInfo = __getFoldedGroupInfo(jsonObj["dynamicStoryScreenInput"]["sentences"], sentencesInfo, okrData)
    jsonObj["dynamicStoryScreenInput"]["foldKeywords"].extend(foldedGroupsInfo)

    return json.dumps(jsonObj, sort_keys=True, indent=4)


def __getFoldedGroupInfo(sentences, sentencesInfo, okrData):
    '''
    Returns the information for the folded groups for the output JSON.
    The list should be extended onto jsonObj["dynamicStoryScreenInput"]["foldKeywords"].
    :param sentences: jsonObj["dynamicStoryScreenInput"]["sentences"]
    :param sentencesInfo:
    :param okrData:
    :return:
    '''

    foldedGroupsInfo = []

    # get the concept IDs used in the unfolded sentences (for keywords lists concstruction):
    conceptIdsInUnfolded = []
    for sentIdx in range(len(sentences)):
        curSentInfo = sentences[sentIdx]
        if curSentInfo["showOnInit"]:
            sentId = curSentInfo["id"]
            conceptIdsInSentence = [conceptInfo['conceptId'] for conceptInfo in sentencesInfo[sentId]['sentenceInfo']]
            conceptIdsInUnfolded.extend(conceptIdsInSentence)
    conceptIdsInUnfolded = set(conceptIdsInUnfolded)

    # build up the folded groups for the closed groups:
    foldedGroup = []
    for sentIdx in range(len(sentences)):
        # for sentenceInfo in sentences:

        # get the current sentence info and the next one if relevant:
        curSentInfo = sentences[sentIdx]
        nextSentInfo = sentences[sentIdx + 1] \
            if sentIdx + 1 < len(sentences) else None

        # if the current sentence should be folded, add it to the current folded group list:
        if not curSentInfo["showOnInit"]:
            foldedGroup.append(curSentInfo["id"])

        # if this is the last folded sentence in the group, get the keywords for the group:
        if (len(foldedGroup) > 0) and (nextSentInfo == None or nextSentInfo["showOnInit"]):
            # get the concpet IDs in the folded sentences:
            conceptsInSentences = []
            for sentId in foldedGroup:
                # get the concpet IDs in the folded sentence:
                conceptsInSent = [conceptInfo['conceptId'] for conceptInfo in sentencesInfo[sentId]['sentenceInfo']]
                # filter out the concepts used in unfolded sentences:
                conceptsInSent = list(set(conceptsInSent) - conceptIdsInUnfolded)
                conceptsInSentences.append(conceptsInSent)

            # conceptsInSentences = [[conceptInfo['conceptId'] for conceptInfo in sentencesInfo[sentId]['sentenceInfo']] \
            #                       for sentId in foldedGroup]
            ## filter out the concepts used in unfolded sentences:
            # conceptsInSentences = list(set(conceptsInSentences) - conceptIdsInUnfolded)
            # get the keywords for the concepts to use for the unfolded sentences:
            keywordsForGroup = Utils.getKeywordsFromConcepts(conceptsInSentences, okrData)
            foldGroupInfo = {"ids": foldedGroup, "keywords": keywordsForGroup}
            foldedGroup = []
            foldedGroupsInfo.append(foldGroupInfo)

        # elif len(foldedGroup) > 0:
        #    conceptsInSentences = [[conceptInfo['conceptId'] for conceptInfo in sentencesInfo[sentId]['sentenceInfo']] for sentId in foldedGroup]
        #    keywordsForGroup = Utils.getKeywordsFromConcepts(conceptsInSentences, okrData)
        #    foldGroupInfo = {"ids":foldedGroup, "keywords":keywordsForGroup}
        #    foldedGroup = []
        #    jsonObj["dynamicStoryScreenInput"]["foldKeywords"].append(foldGroupInfo)

    return foldedGroupsInfo


def _getUsefulConceptIds(sentencesInfo):
    '''
    Returns a list of conceptIDs used more than once throughout all sentences.
    :param sentencesInfo:
    :return:
    '''
    conceptsCounts = {}
    for sentInfo in sentencesInfo.values():
        for conExpInfo in sentInfo['sentenceInfo']:
            conceptId = conExpInfo['conceptId']
            conceptsCounts[conceptId] = conceptsCounts.get(conceptId, 0) + 1

    return [conceptId for conceptId, conceptCount in conceptsCounts.iteritems() if conceptCount > 1]