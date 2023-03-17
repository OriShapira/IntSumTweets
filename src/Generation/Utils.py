import numpy as np
import sklearn.cluster
import editdistance
from stemming.porter2 import stem
import operator


PREPOSITIONS = {'aboard':1, 'about':1, 'above':1, 'absent':1, 'across':1, 'cross':1, 'after':1, 'against':1, 'again':1, 'along':1, 'alongst':1, 'alongside':1, 'amid':1, 'amidst':1, 'among':1, 'amongst':1, 'apropos':1, 'apud':1, 'around':1, 'as':1, 'astride':1, 'at':1, 'atop':1, 'ontop':1, 'bar':1, 'before':1, 'b4':1, 'behind':1, 'below':1, 'beneath':1, 'beside':1, 'besides':1, 'between':1, 'beyond':1, 'but':1, 'by':1, 'circa':1, 'come':1, 'despite':1, 'down':1, 'during':1, 'except':1, 'for':1, 'from':1, 'in':1, 'inside':1, 'into':1, 'less':1, 'like':1, 'minus':1, 'near':1, 'nearest':1, 'notwithstanding':1, 'of':1, 'off':1, 'on':1, 'onto':1, 'opposite':1, 'out':1, 'outside':1, 'over':1, 'past':1, 'per':1, 'sans':1, 'since':1, 'than':1, 'through':1, 'thru':1, 'throughout':1, 'to':1, 'toward':1, 'towards':1, 'under':1, 'underneath':1, 'unlike':1, 'until':1, 'till':1, 'up':1, 'upon':1, 'upside':1, 'versus':1, 'via':1, 'vis-a-vis':1, 'with':1, 'within':1, 'without':1, 'ago':1, 'apart':1, 'aside':1, 'away':1, 'hence':1, ',':1, '?':1 }
STOP_WORDS = {'a':1, 'about':1, 'above':1, 'across':1, 'after':1, 'afterwards':1, 'again':1, 'against':1, 'all':1, 'almost':1, 'alone':1, 'along':1, 'already':1, 'also':1,'although':1,'always':1,'am':1,'among':1, 'amongst':1, 'amoungst':1, 'amount':1,  'an':1, 'and':1, 'another':1, 'any':1,'anyhow':1,'anyone':1,'anything':1,'anyway':1, 'anywhere':1, 'are':1, 'around':1, 'as':1,  'at':1, 'back':1,'be':1,'became':1, 'because':1,'become':1,'becomes':1, 'becoming':1, 'been':1, 'before':1, 'beforehand':1, 'behind':1, 'being':1, 'below':1, 'beside':1, 'besides':1, 'between':1, 'beyond':1, 'bill':1, 'both':1, 'bottom':1,'but':1, 'by':1, 'call':1, 'can':1, 'cannot':1, 'cant':1, 'co':1, 'con':1, 'could':1, 'couldnt':1, 'cry':1, 'de':1, 'describe':1, 'detail':1, 'do':1, 'done':1, 'down':1, 'due':1, 'during':1, 'each':1, 'eg':1, 'eight':1, 'either':1, 'eleven':1,'else':1, 'elsewhere':1, 'empty':1, 'enough':1, 'etc':1, 'even':1, 'ever':1, 'every':1, 'everyone':1, 'everything':1, 'everywhere':1, 'except':1, 'few':1, 'fifteen':1, 'fify':1, 'fill':1, 'find':1, 'fire':1, 'first':1, 'five':1, 'for':1, 'former':1, 'formerly':1, 'forty':1, 'found':1, 'four':1, 'from':1, 'front':1, 'full':1, 'further':1, 'get':1, 'give':1, 'go':1, 'had':1, 'has':1, 'hasnt':1, 'have':1, 'he':1, 'hence':1, 'her':1, 'here':1, 'hereafter':1, 'hereby':1, 'herein':1, 'hereupon':1, 'hers':1, 'herself':1, 'him':1, 'himself':1, 'his':1, 'how':1, 'however':1, 'hundred':1, 'ie':1, 'if':1, 'in':1, 'inc':1, 'indeed':1, 'interest':1, 'into':1, 'is':1, 'it':1, 'its':1, 'itself':1, 'keep':1, 'last':1, 'latter':1, 'latterly':1, 'least':1, 'less':1, 'ltd':1, 'made':1, 'many':1, 'may':1, 'me':1, 'meanwhile':1, 'might':1, 'mill':1, 'mine':1, 'more':1, 'moreover':1, 'most':1, 'mostly':1, 'move':1, 'much':1, 'must':1, 'my':1, 'myself':1, 'name':1, 'namely':1, 'neither':1, 'never':1, 'nevertheless':1, 'next':1, 'nine':1, 'no':1, 'nobody':1, 'none':1, 'noone':1, 'nor':1, 'not':1, 'nothing':1, 'now':1, 'nowhere':1, 'of':1, 'off':1, 'often':1, 'on':1, 'once':1, 'one':1, 'only':1, 'onto':1, 'or':1, 'other':1, 'others':1, 'otherwise':1, 'our':1, 'ours':1, 'ourselves':1, 'out':1, 'over':1, 'own':1,'part':1, 'per':1, 'perhaps':1, 'please':1, 'put':1, 'rather':1, 're':1, 'same':1, 'see':1, 'seem':1, 'seemed':1, 'seeming':1, 'seems':1, 'serious':1, 'several':1, 'she':1, 'should':1, 'show':1, 'side':1, 'since':1, 'sincere':1, 'six':1, 'sixty':1, 'so':1, 'some':1, 'somehow':1, 'someone':1, 'something':1, 'sometime':1, 'sometimes':1, 'somewhere':1, 'still':1, 'such':1, 'system':1, 'take':1, 'ten':1, 'than':1, 'that':1, 'the':1, 'their':1, 'them':1, 'themselves':1, 'then':1, 'thence':1, 'there':1, 'thereafter':1, 'thereby':1, 'therefore':1, 'therein':1, 'thereupon':1, 'these':1, 'they':1, 'thickv':1, 'thin':1, 'third':1, 'this':1, 'those':1, 'though':1, 'three':1, 'through':1, 'throughout':1, 'thru':1, 'thus':1, 'to':1, 'together':1, 'too':1, 'top':1, 'toward':1, 'towards':1, 'twelve':1, 'twenty':1, 'two':1, 'un':1, 'under':1, 'until':1, 'up':1, 'upon':1, 'us':1, 'very':1, 'via':1, 'was':1, 'we':1, 'well':1, 'were':1, 'what':1, 'whatever':1, 'when':1, 'whence':1, 'whenever':1, 'where':1, 'whereafter':1, 'whereas':1, 'whereby':1, 'wherein':1, 'whereupon':1, 'wherever':1, 'whether':1, 'which':1, 'while':1, 'whither':1, 'who':1, 'whoever':1, 'whole':1, 'whom':1, 'whose':1, 'why':1, 'will':1, 'with':1, 'within':1, 'without':1, 'would':1, 'yet':1, 'you':1, 'your':1, 'yours':1, 'yourself':1, 'yourselves':1, 'the':1}
ATTRIBUTION_STRS = [ ':' , '|' , '-' , '>' ] # , 'say' , 'says' , 'said', 'reports' , 'reported' , 'report' ]
PRONOUNS = {'I':1, 'you':1, 'he':1, 'she':1, 'it':1, 'we':1, 'they':1, 'me':1, 'him':1, 'her':1, 'us':1, 'them':1, 'mine':1, 'yours':1, 'his':1, 'hers':1, 'ours':1, 'theirs':1, 'this':1, 'these':1, 'those':1, 'who':1, 'whom':1, 'whose':1, 'which':1, 'that':1, 'what':1, 'whatever':1, 'whoever':1, 'whomever':1, 'whichever':1, 'myself':1, 'yourself':1, 'himself':1, 'herself':1, 'itself':1, 'ourselves':1, 'themselves':1}

'''
Clustering constants below:
'''
# The threshold for putting a candidate proposition into a cluster:
THRESHOLD_CLUSTER_SCORE_DEFAULT = 0.5

# The linear weights of the individual scores in the function of the clustering score:
CLUSTER_PREDICATES_SCORE_WEIGHT = 1.0
CLUSTER_ARGS_SCORE_WEIGHT = 1.0

# The linear weights of the individual scores in the function of the cluster representative retrieval score:
REPRESENTATIVE_PROP_CONCEPTIDS_SCORE_WEIGHT = 1.0
REPRESENTATIVE_PROP_PREDWORDS_SCORE_WEIGHT = 1.0
REPRESENTATIVE_PROP_SIZE_SCORE_WEIGHT = 1.0


def reduceSimilarWords(wordsList):
    '''
    Returns a reduced list of words getting rid of very similar instances.
    Clusters together the words and returns the cluster centers.
    Source: https://stats.stackexchange.com/questions/123060/clustering-a-long-list-of-strings-words-into-similarity-groups
    :param wordsList:
    :return:
    '''
    # no need to reduce a list with 0 or 1 words:
    if len(wordsList) <= 1:
        return wordsList

    # only use the stems of the words list (and keep a mapping):
    stemMapping = {}
    for word in wordsList:
        if word != '':
            stemWord = stem(word)
            if not stemWord in stemMapping:
                stemMapping[stemWord] = []
            stemMapping[stemWord].append(word)
    stems = stemMapping.keys()

    # prepare the words list:
    #wordsUniqueList = list(set(wordsList)) # get rid of duplicates
    wordsUniqueList = list(set(stems))  # get rid of duplicates
    words = np.asarray(wordsUniqueList)

    # no need to reduce a list with 0 or 1 words:
    if len(words) == 1:
        return [min((word for word in stemMapping[words[0]] if word), key=len)]

    # prepare the edit distance matrix:
    ed_similarity = -1 * np.array([[editdistance.eval(w1, w2) for w1 in words] for w2 in words])

    # cluster:
    reducedList = []
    affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
    affprop.fit(ed_similarity)
    for cluster_id in np.unique(affprop.labels_):
        exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
        reducedList.append(exemplar)
        #cluster = np.unique(words[np.nonzero(affprop.labels_ == cluster_id)])
        #cluster_str = ", ".join(cluster)
        #print(" - *%s:* %s" % (exemplar, cluster_str))

    # now for each stem, get the shortest word in its list:
    finalWordList = [min((word for word in stemMapping[stemWord] if word), key=len) for stemWord in reducedList]

    return finalWordList


def reduceSentenceExpansionList(expansionList):
    listToUse = []

    # flag phrases contained in other phrases (to remove them):
    removeList = []
    for ind1 in range(len(expansionList)):
        phrase1 = expansionList[ind1]
        # don't bother on phrases already removed:
        if phrase1 in removeList:
            continue
        p1 = phrase1.lower().strip(' ,.:;\'\"')
        for ind2 in range(len(expansionList)):
            if ind1 != ind2:
                p2 = expansionList[ind2].lower().strip(' ,.:;\'\"')
                # if phrase1 is contained in phrase2, put it in the remove list:
                if p1 in p2:
                    removeList.append(phrase1)
                    break

    # now remove the flagged phrases:
    for phrase in removeList:
        expansionList.remove(phrase)

    # count up the stems in all words of all phrases:
    stemsCounts = {}
    for phrase in expansionList:
        words = phrase.split()
        for word in words:
            stemWord = stem(word)
            stemsCounts[stemWord] = stemsCounts.get(stemWord, 0) + 1

    # see what the counts of each one is now:
    phraseScores = {}
    for phrase in expansionList:
        phraseCounts = []
        words = phrase.split()
        for word in words:
            stemWord = stem(word)
            phraseCounts.append(stemsCounts[stemWord])

        # if there's a word in the phrase that is unique, use the phrase:
        if min(phraseCounts) == 1:
            listToUse.append(phrase)
        else: # give the phrase a score
            phraseScores[phrase] = sum(phraseCounts)

    # use the best-k phrases (lowest scores -> more unique words):
    # sort by score (lowest is best):
    phraseScores_sorted = sorted(phraseScores.items(), key=operator.itemgetter(1))
    # take the best scoring phrases until 7 are filled (and if more have been filled, don't use any [hence the max]):
    listToUse.extend([phrase for phrase, _ in phraseScores_sorted][0 : max(min(len(expansionList), 7)-len(listToUse), 0)])

    # only keep phrases longer than 7 characters:
    listToUse = [phrase for phrase in listToUse if len(phrase) > 7]

    return listToUse


def getKeywordsFromConcepts(conceptsLists, okrData):
    '''
    Returns a list of keywords from the given lists of conceptID lists.
    :param conceptsLists: List of lists of concept IDs.
    :return: List of words.
    '''

    conceptCount = {}
    for list in conceptsLists:
        for conceptId in list:
            conceptCount[conceptId] = conceptCount.get(conceptId, 0) + 1

    conceptCountSorted = sorted(conceptCount.items(), key=operator.itemgetter(1), reverse=True)

    keywordsList = [okrData.getKeywordRepresentation(conceptId) for conceptId, _ in conceptCountSorted]
    keywordsList = filter(lambda a: a != '' and not 'IMPLICIT' in a, keywordsList) # remove empty strings and those with IMPLICIT
    return keywordsList