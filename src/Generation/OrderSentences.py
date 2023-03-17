import time
import operator
import numpy as np

def orderSentences(sentencesInfo, okrData):
    '''
    Calculates the order of the given sentences (from top to bottom).
    :param sentencesInfo: A dictionary of dictionaries { key is sentence ID, value is {
            'sentence':<full string>,
            'tweets':<list of tweets>,
            'sentenceExpansion':<list of strings>,
            'conceptExpansions':<dictionary of {argId:<list of strings>}>,
            'sentenceInfo':<the information list about the sentence (list of {'indices':<list>, 'conceptId':<id>})>,
            'clusterPropIds':<list of propIDs in the cluster of this sentence>,
            'clusterRepPropId':<the propID of the proposition representing the cluster> } }
    :return: A list of dictionaries in order from top to bottom with {
            'sentenceId':<the ID of the sentence>,
            'timestamp':<the timestamp for the sentence>,
            'fold':<True of False> }
    '''
    sentencesTimes = _getTimestampsOfSentences(sentencesInfo, okrData)
    sentIdsOrderedList = _orderByTime(sentencesTimes)
    sentFolding = _decideFolding(sentencesInfo, okrData)

    return [{'sentenceId':sentId, 'timestamp':sentencesTimes[sentId], 'fold':sentFolding[sentId]} for sentId in sentIdsOrderedList]


def _getTimestampsOfSentences(sentencesInfo, okrData):
    '''
    For each sentence, calculates the average time of all of its tweets.
    :param sentencesInfo:
    :param okrData:
    :return: A dictionary of sentence ID to timestamp.
    '''
    sentencesTimes = {}
    for sentId, sentInfo in sentencesInfo.iteritems():
        allSentenceTimestamps = map(lambda tsStr: time.mktime(time.strptime(tsStr, "%Y-%m-%d %H:%M:%S")),
                                       [okrData.tweets[tweetId].timestamp for tweetId in sentInfo['tweets']
                                        if tweetId in okrData.tweets and okrData.tweets[tweetId].timestamp != None])

        # use the average times of the tweets of the sentence:
        #avg_time = time.localtime(reduce(lambda x, y: x + y, allSentenceTimestamps) / len(allSentenceTimestamps))
        #sentenceTime = avg_time

        # use the earliest time of the tweets of the sentence:
        earliest_time = time.localtime(min(allSentenceTimestamps))
        sentenceTime = earliest_time

        avg_time_str = time.strftime("%Y-%m-%d %H:%M:%S", sentenceTime)
        sentencesTimes[sentId] = avg_time_str

    return sentencesTimes

def _orderByTime(sentencesTimes):
    '''
    Returns a list of sentence IDs ordered by descending time (latest first).
    :param sentencesTimes: Dictionary of sentenceID to timestamp string
    :return:
    '''
    # convert the string timestamps to time objects:
    sentencesTimestamps = {sentId : time.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                           for sentId, ts_str in sentencesTimes.iteritems()}
    # sort the sentId,timestamp pairs by time (earliest first): #(latest first):
    sentencesOrder = sorted(sentencesTimestamps.items(), key=operator.itemgetter(1))#, reverse=True)

    return [sentId for sentId, _ in sentencesOrder]

def _decideFolding(sentencesInfo, okrData):
    '''
    Gives each sentence an indicator whether it should be folded or not.
    :param sentencesInfo:
    :return: A dictionary of sentence ID to boolean.
    '''

    # give each sentence a folding score:
    sentScores = {}
    for sentId, sentInfo in sentencesInfo.iteritems():
        numTweets = len(sentInfo['tweets'])
        numSentExpansions = len(sentInfo['sentenceExpansion'])
        sentLen = len(sentInfo['sentence'].split())

        tweetsScore = float(numTweets) / float(len(okrData.tweets))
        sentExpScore = float(numSentExpansions) / float(len(okrData.entities)+len(okrData.propositions))
        sentLenScore = float(sentLen) / 20.0

        sentScores[sentId] = (0.33 * tweetsScore) + (0.33 * sentExpScore) + (0.33 * sentLenScore)
        # TODO: Take similar information into acount (similar info in other sentences should get lower score)


    # Use the top 10 sentences:

    # order sentence IDs by score:
    sortedSentences = sorted(sentScores.items(), key=lambda kv: kv[1], reverse=True)

    # choose the top 10 sentences:
    sentFolding = {}
    numSentencesToShow = 7
    for i in range(len(sortedSentences)):
        sentId = sortedSentences[i][0]
        if i < numSentencesToShow:
            sentFolding[sentId] = False # don't fold the top k sentences
        else:
            sentFolding[sentId] = True # fold the top k sentences

    #topSentenceId = sortedSentences[0][0]
    #print(sentencesInfo[topSentenceId]['sentence'])

    '''
    # Fold all those below the median score:

    # find the median score of the sentences -- this is the threshold:
    medianScore = np.median(sentScores.values())

    # all sentences with a score below the threshold should be set as foldable:
    sentFolding = {}
    for sentId, sentScore in sentScores.iteritems():
        sentFolding[sentId] = sentScore <= medianScore
    '''

    return sentFolding