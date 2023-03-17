import editdistance
from munkres import Munkres

import Utils


def getPropositionClusters(okrData, clusterScoreThreshold=Utils.THRESHOLD_CLUSTER_SCORE_DEFAULT):
    '''
    Clusters the propositions together according to similarity of predicates and arguments.
    :param okrData:
    :param clusterScoreThreshold: Optional - the threshold score for put a candidate in a cluster.
    :return: A list of lists of proposition IDs (each list is a cluster), and a list of representative propIDs for each cluster.
    '''

    clusters = [] # list of lists of propIds

    for propId in okrData.propositionIDs:
        _putInBestCluster(okrData, propId, clusters, clusterScoreThreshold)

    clusterRepresentatives = _getClusterRepresentatives(okrData, clusters)

    return clusters, clusterRepresentatives


def _putInBestCluster(okrData, candidatePropId, clusters, clusterScoreThreshold):
    # find the cluster that best matches:
    bestClusterIndex = -1
    bestClusterScore = -1
    for clusterIdx, cluster in enumerate(clusters):
        similarityScore = _getClusterMatchScore(okrData, cluster, candidatePropId)
        if similarityScore > bestClusterScore:
            bestClusterIndex = clusterIdx
            bestClusterScore = similarityScore

    # put the propID in the best cluster (or a new one if the threshold is not passed):
    if bestClusterScore > clusterScoreThreshold:
        clusters[bestClusterIndex].append(candidatePropId)
    else:
        clusters.append([candidatePropId]) # new cluster - candidate is not similar enough to the rest


def _getClusterMatchScore(okrData, clusterPropIds, candidatePropId):
    '''
    Calculates a similarity score between the given candidate proposition and the cluster given.
    :param okrData:
    :param clusterPropIds:
    :param candidatePropId:
    :return:
    '''

    # get the candidate proposition's predicate counters and argument concept counters:
    predicateStemsCountersCandidate = okrData.propositions[candidatePropId].getAllPredicateStemsNonStopWords()
    conceptsIdsCountersCandidate = {conceptId:len(argsList) for conceptId, argsList in okrData.propositions[candidatePropId].getConceptIdsAsArgs().iteritems()}

    maxScoreInCluster = -1
    for propId in clusterPropIds:
        # get the current member proposition's predicate counters and argument concept counters:
        predicateStemsCountersMember = okrData.propositions[propId].getAllPredicateStemsNonStopWords()
        conceptsIdsCountersMember = {conceptId: len(argsList) for conceptId, argsList in okrData.propositions[propId].getConceptIdsAsArgs().iteritems()}

        # get the similarity between the candidate and the current member:
        predicatesScore = _predicatesMatchingScore(predicateStemsCountersCandidate, predicateStemsCountersMember)
        argumentsScore = _argumentsMatchingScore(conceptsIdsCountersCandidate, conceptsIdsCountersMember)
        simScore = ((Utils.CLUSTER_PREDICATES_SCORE_WEIGHT * predicatesScore) + (
            Utils.CLUSTER_ARGS_SCORE_WEIGHT * argumentsScore)) / \
                   (Utils.CLUSTER_PREDICATES_SCORE_WEIGHT + Utils.CLUSTER_ARGS_SCORE_WEIGHT) # the average of the predicate and arguments score

        # keep the best score found within the cluster:
        if simScore > maxScoreInCluster:
            maxScoreInCluster = simScore

    return maxScoreInCluster

def _argumentsMatchingScore(argsCounter1, argsCounter2):
    # Give a score for intersecting arguments between the two given dictionaries (taking their count into account).
    # The score is between 0 (not similar) and 1 (the same proportionally).
    # Get the proportion of intersecting args in each group and average it.
    # Example: [a]2 [b]3  <>  [b]4 [c]2 [d]1  ->  average of 3/5 and 4/7

    # make new counters where propostitions are 1.5 stronger:
    argsWeights1 = {conc: count * 1.5 if conc[0] == 'P' else count for conc, count in argsCounter1.iteritems()}
    argsWeights2 = {conc: count * 1.5 if conc[0] == 'P' else count for conc, count in argsCounter2.iteritems()}

    fullCount1 = sum(argsWeights1.values())
    fullCount2 = sum(argsWeights2.values())

    intersectingCount1 = 0
    intersectingCount2 = 0
    for conceptId in argsWeights1:
        if conceptId in argsWeights2:
            intersectingCount1 += argsWeights1[conceptId]
            intersectingCount2 += argsWeights2[conceptId]

    # average of the two ratios
    ratio1 = float(intersectingCount1) / float(fullCount1)
    ratio2 = float(intersectingCount2) / float(fullCount2)

    return (ratio1 + ratio2) / 2



def _predicatesMatchingScore(wordCounters1, wordCounters2):
    # Give a score for similarities between the words in the two given dictionaries (taking their count into account).
    # The score is between 0 (not similar) and 1 (the same proportionally).
    # First best matches the two lists of words using edit distance, and then for each pair calculates
    # their proportional distance and their proportional frequency ratio.
    # Then returns the average of all the pairs.
    # Source for matching algorithm:
    #   https://stackoverflow.com/questions/26990714/algorithm-for-fuzzy-pairing-of-strings-from-two-lists/26993195#26993195

    fullCount1 = sum(wordCounters1.values()) # the total number of words throughout the whole group
    fullCount2 = sum(wordCounters2.values()) # the total number of words throughout the whole group

    # if there are no words to compare, just return a score of zero:
    if fullCount1 == 0 and fullCount2 == 0:
        return 0

    list1 = [word for word in wordCounters1]
    list2 = [word for word in wordCounters2]

    # extend the short list with empty strings so that the two have an equal number of strings:
    if len(list1) < len(list2):
        list1.extend([''] * (len(list2) - len(list1)))
    elif len(list1) > len(list2):
        list2.extend([''] * (len(list1) - len(list2)))

    # build the distances matrix between the two lists (using edit distance):
    distanceMatrix = []
    for w1 in list1:
        row = []
        for w2 in list2:
            row.append(editdistance.eval(w1.lower(), w2.lower()))
        distanceMatrix.append(row)

    # find the word pairs that best match by getting the matrix locations with minimum value in each row:
    munkres = Munkres() # implementation of the Kuhn-Munkres algorithm (Hungarian algorithm), for solving the Assignment Problem.

    scores = []
    for idx1, idx2 in munkres.compute(distanceMatrix):
        word1 = list1[idx1]
        word2 = list2[idx2]
        if word1 != '' and word2 != '':
            # the edit distance between the two words:
            distance = distanceMatrix[idx1][idx2]

            # the average ratio of the proportional frequencies of the words in their group:
            ratio1 = float(wordCounters1[word1]) / float(fullCount1) # the proportion of word1 in group1
            ratio2 = float(wordCounters2[word2]) / float(fullCount2) # the proportion of word2 in group2
            ratio = (ratio1 + ratio2) / 2

            # (The distance in proportion to the length of the longer word)
            # times the ratio of the frequencies of the two words
            # Example: 'abcd' (4 of 10) <> 'ad' (2 of 8)  ->  ((4-2)/4)*0.325=0.1625
            maxLenWord = max(len(word1), len(word2))
            score = (float(maxLenWord - distance) / maxLenWord) * ratio
            #score = (float(maxLenWord - distance) / maxLenWord)
            scores.append(score)
        else:
            scores.append(0.)

    # the average of the scores within all matching pairs is the final score:
    #finalScore = reduce(lambda x, y: x + y, scores) / len(scores)
    finalScore = max(scores)

    return finalScore


def _getClusterRepresentatives(okrData, clusters):
    '''
    For each cluster, sets a propID that represents it.
    :param okrData:
    :param clusters:
    :return:
    '''
    clusterReps = []
    for cluster in clusters:
        clusterRepPropId = _getCluterRepresentative(okrData, cluster)
        clusterReps.append(clusterRepPropId)

    return clusterReps

def _getCluterRepresentative(okrData, cluster):
    # for each propositions, set a score as a function of:
    #   inter-prop count of arguments
    #   inter-prop count of predicates (including prepositions)
    #   number of templates in prop

    # if the cluster has just one proposition, it will be the representative:
    if len(cluster) == 1:
        return cluster[0]

    # count up in how many propositions each argument conceptId and predicate word is used (this is their score):
    conceptIdsCount = {}
    predicateWordsCount = {}
    for propId in cluster:
        conceptIds = okrData.propositions[propId].getConceptIdsAsArgs().keys()
        for conceptId in conceptIds:
            conceptIdsCount[conceptId] = conceptIdsCount.get(conceptId, 0) + 1
        predicateWords = okrData.propositions[propId].getAllPredicateStemsNonStopWords().keys() + \
                         okrData.propositions[propId].getAllPredicateStopWords().keys()
        for predicateWord in predicateWords:
            predicateWordsCount[predicateWord] = predicateWordsCount.get(predicateWord, 0) + 1

    # sum up the scores of contained arg conceptsIDs and predicate words:
    bestScore = -1
    bestPropId = None
    for propId in cluster:
        conceptIds = okrData.propositions[propId].getConceptIdsAsArgs().keys()
        predicateWords = okrData.propositions[propId].getAllPredicateStemsNonStopWords().keys() + \
                         okrData.propositions[propId].getAllPredicateStopWords().keys()

        conceptIdsScore = sum([conceptIdsCount[conceptId] for conceptId in conceptIds]) # commonness of concepts in args
        predWordsScore = sum([predicateWordsCount[predWord] for predWord in predicateWords]) # commonness of pred words score
        sizeScore = len(okrData.propositions[propId].templates) # number of templates in the proposition

        totalPropScore = (Utils.REPRESENTATIVE_PROP_CONCEPTIDS_SCORE_WEIGHT * conceptIdsScore) + \
                         (Utils.REPRESENTATIVE_PROP_PREDWORDS_SCORE_WEIGHT * predWordsScore) + \
                         (Utils.REPRESENTATIVE_PROP_SIZE_SCORE_WEIGHT * sizeScore)

        if totalPropScore > bestScore:
            bestScore = totalPropScore
            bestPropId = propId

    return bestPropId