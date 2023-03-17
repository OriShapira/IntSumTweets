import operator

from nltk.corpus import stopwords
from stemming.porter2 import stem

import IntraPropositionMerge
import Utils


class Argument:

    def __init__(self, containerPropId, argId, argDescription):
        self.containerPropId = containerPropId
        self.argIdInContainerProposition = argId
        self.argDescription = argDescription
        self.conceptIDs = {} # the mentions used in the argument key:conceptId, value:list of tweets where it is used

    def addArgMention(self, conceptId, tweetsList):
        if conceptId in self.conceptIDs:
            self.conceptIDs[conceptId].extend(tweetsList)
        else:
            self.conceptIDs[conceptId] = tweetsList

    def getConceptIdForTweetId(self, tweetId):
        for conceptId, tweetIds in self.conceptIDs.iteritems():
            if tweetId in tweetIds:
                return conceptId
        return None

    def getMostCommonConceptId(self):
        conceptId = max(self.conceptIDs, key=lambda x: len(self.conceptIDs[x]))
        tweetId = self.conceptIDs[conceptId][0] # for now just take the first tweet ID in the list of the concept
        return conceptId, tweetId

    def getTweetIdsOfConcept(self, conceptId, getDefaultIfNotExists):
        '''
        Gets the tweetIDs list for the conceptID specified.
        If the conceptID is not use in this argument and getDefaultIfNotExists is True, gets a random concept used
        in the argument.
        :param conceptId: The concept ID for which to get its source tweets.
        :param getDefaultIfNotExists: Whether or not to use a different concept if the specified one isn;t here.
        :return: The conceptID actually used, and the list of tweet IDs in which this concept was used in this argument. Or None, None if none found.
        '''
        if conceptId in self.conceptIDs:
            return conceptId, self.conceptIDs[conceptId]
        elif getDefaultIfNotExists:
            return self.conceptIDs.iteritems().next()
        return None, None

    def getConceptExpansionStrs(self):
        '''
        Returns all the basic strings of the concepts used in this argument.
        The argument could have more than one concept used in its slot, and each such concept has several
        strings used to express it.
        :return: The list of strings, and the list of conceptIDs from which they originate.
        '''
        allStrs = []
        for conceptId in self.conceptIDs:
            conceptStrs = okrData.getConceptStrings(conceptId)
            allStrs.extend(conceptStrs)
            if 'IMPLICIT' in allStrs:
                allStrs.remove('IMPLICIT')
        return allStrs, self.conceptIDs.keys()


class Template:

    ARG = 0
    PRED = 1

    def __init__(self, parentPropId, templateStr, tweetsList):
        # the id of the proposition that this template is a mention of
        self.parentPropId = parentPropId
        # The template string in full (argIDs not replaced)
        self.str_basic = None
        # The template string in full (argIDs replaced with slot strings) for each tweetId
        self.str_full = {}
        # The information about the template string.
        # For each tweetId used to generate the string, keep a data structure of info on the string.
        # The ds is a list of dictionaries containing {'indices':<list of indices>, 'conceptId':<the one used>, 'argId':<the argument ID (if it is an argument)>}
        self.str_full_info = {}
        # The parts of the template:
        # list of (<TYPE>, <INDEX>) where <TYPE> is 'ARG' or 'PRED' and index
        # is index in the args of predicates arrays
        self.parts = []
        # The arguments in the template:
        # list of dictionaries of information ({'indexInTemplate', 'argID', 'argObj':<arg object>, 'str', 'info':<the concept information of the arg>})
        self.args = []
        # The preciates in the template:
        # list of dictionaries of information ({'indexInTemplate', 'str':<predicate word string>})
        self.predicates = []
        # To link argument ID to its index in the args list
        self.argsMap = {}
        # The integer list of tweet id in which this template occurs
        self.tweetsList = tweetsList

        # parse the input information:
        self._parseTemplateStr(templateStr)

    def _parseTemplateStr(self, templateStr):
        '''
        Converts a string from the input file to the template parts.
        Format example: <a.1.2> went to <a.1.1>
        :param templateStr:
        :return:
        '''
        predTemplateParts = templateStr.split(' ')
        predTemplatePartsUpdated = []
        predNum = 0
        argNum = 0

        for partIdx, part in enumerate(predTemplateParts):

            # if this is an argument (startswith '<' and endswith '>')
            if (part[0] == '<' and part[-1] == '>') or (part[0] == '{' and part[-1] == '}'):
                # replace the argIDs in the template from <a.x.y> to [y]
                argId = int(part[1:-1].split('.')[-1])  # take the last part of <a.x.y> split on '.' (without the <>)
                predTemplatePartsUpdated.append('[{}]'.format(argId))

                self.args.append({'indexInTemplate': partIdx, 'argID': argId, 'argObj': None, 'str':'', 'info':None}) # object string and info of arg to be filled later
                self.argsMap[argId] = argNum
                self.parts.append((Template.ARG, argNum))
                argNum += 1

            # this is a predicate word
            else:
                # if the predicate is the 'IMPLICIT' string, then just add the two arguments (not in the template string):
                if part == 'IMPLICIT':
                    predTemplatePartsUpdated.append('[{}]'.format(1))
                    predTemplatePartsUpdated.append('[{}]'.format(2))

                    self.args.append({'indexInTemplate': 0, 'argID': 1, 'argObj': None, 'str': ''})
                    self.args.append({'indexInTemplate': 1, 'argID': 2, 'argObj': None, 'str': ''})
                    self.argsMap[1] = 0
                    self.argsMap[2] = 1
                    self.parts.append((Template.ARG, 0))
                    self.parts.append((Template.ARG, 1))

                    partIdx = 2

                # this isn't an argument, just append it as the next word in the sentence:
                predTemplatePartsUpdated.append(part)

                self.predicates.append({'indexInTemplate': partIdx, 'str': part})
                self.parts.append((Template.PRED, predNum))
                predNum += 1

        # rewrite the template with the updated arguments representation:
        self.str_basic = ' '.join(predTemplatePartsUpdated)

    def setArgument(self, argId, argObject):
        argIdx = self.argsMap[argId]
        self.args[argIdx]['argObj'] = argObject

        ## use some concept's representing string for the argument slot:
        #self.args[argIdx]['str'] = okrData.getRepresentingString(argObject.conceptIDs.keys()[0])

    def hasArgument(self, argId):
        return argId in self.argsMap

    def isImplicit(self):
        for predInfo in self.predicates:
            if predInfo['str'] != 'IMPLICIT':
                return False
        return True

    def isStopWordsOnly(self):
        for predStr in self.predicates:
            if not predStr['str'] in Utils.STOP_WORDS:
                return False
        return True

    def isAttrubution(self):
        # if the proposition is a known attribution, it's obvious:
        if okrData.propositions[self.parentPropId].attributor != None:
            return True

        # otherwise check for specific attribution strings:
        for predInfo in self.predicates:
            if not predInfo['str'] in Utils.ATTRIBUTION_STRS:
                return False
        return True

    def isPrepostionsOnly(self):
        for pred in self.predicates:
            if not pred['str'] in Utils.PREPOSITIONS:
                return False
        return True

    def getPrepositionBeforeArgs(self):
        # Returns a dictionary of arg->preposition for all args in the template that have a preposition before it.

        argsPrep = {}
        for argId in self.argsMap:
            prep = self.getPrepositionBeforeArg(argId)
            if prep != None:
                argsPrep[argId] = prep
        return argsPrep

    def getPrepositionBeforeArg(self, argId):
        prepositionBefore = None

        argIdxInTemplate = self.argsMap[argId] # get index of argument in the template parts
        # if the index of the argument is not in the beginning, check the preceding part:
        if argIdxInTemplate > 0:
            partType, partIdx = self.parts[argIdxInTemplate - 1]
            # if the preceding type is a predicate, and the word is a proposition, use it:
            if partType == Template.PRED and self.predicates[partIdx]['str'] in Utils.PREPOSITIONS:
                prepositionBefore = self.predicates[partIdx]['str']

        return prepositionBefore

    def getPredicateWordsNonStopWords(self):
        return [predInfo['str'] for predInfo in self.predicates if predInfo['str'] not in Utils.STOP_WORDS]

    def getPredicateWordsStopWords(self):
        return [predInfo['str'] for predInfo in self.predicates if predInfo['str'] in Utils.STOP_WORDS]

    def getPredicateBasicStr(self):
        return ' '.join(self.getPredicateWordsNonStopWords())

    def __len__(self):
        return len(self.parts)

    def __str__(self):
        return self.getFullStr(self.tweetsList[0])[0]

    def getFullStr(self, tweetIdToUse=None):
        '''
        Gets the template string and the information about it taking the tweet ID specified into account when
        generating the sentence.
        :param tweetIdToUse:
        :return: A string, and a list of parts information {'conceptId', 'indices', 'expansion', 'argId'-optional}
        '''

        # if no source tweet ID is provided, just use the first one:
        if tweetIdToUse == None:
            tweetIdToUse = self.tweetsList[0]

        # if the sentence for the tweetID was not created yet, then generate it now:
        if not tweetIdToUse in self.str_full:
            # put the representing strings in the arg slots:
            for arg in self.args:
                conceptIdToUse = arg['argObj'].getConceptIdForTweetId(tweetIdToUse)
                # if the template in the tweet ID specified does not have this argument, skip it:
                if conceptIdToUse != None:
                    # (this is essentially the recursion for nested propositions):
                    arg['str'], arg['info'] = okrData.getRepresentingString(conceptIdToUse, tweetIdToUse)
                    # if the argument is an entity, put the concept expansion for it:
                    # Note: For entity arguments, all argument corefering mentions are placed in the expansion.
                    #       For proposition arguments, only the proposition coreferring templates are used.
                    #       These are gotten from the above getRepresentingString call.
                    if conceptIdToUse.startswith('E'):
                        # get a reduced list of a unique list of concepts for the argument:
                        argStrs, concepts = arg['argObj'].getConceptExpansionStrs()
                        argStrs = Utils.reduceSimilarWords(list(set(argStrs)))
                        if arg['str'] in argStrs:
                            argStrs.remove(arg['str']) # remove the arg value itself from the expansion
                        if len(argStrs) > 0:
                            arg['info'][0]['expansion'] = argStrs


            strs = [] # the sentence words to append
            strIndex = 0 # the current word index in the sentence
            # the information about the different parts of the sentence:
            strInfo = [{'conceptId':self.parentPropId, 'indices':[], 'expansion':[]}] # get ready with this predicate itself

            if not self.isImplicit():
                # loop through the parts of the sentence:
                for partType, partIdx in self.parts:
                    if partType == Template.ARG:
                        # append the substring for the argument:
                        #strs.append('[' + self.args[partIdx]['str'] + ']')
                        strs.append(self.args[partIdx]['str'])

                        # extend the information about the words in the substring of the argument:
                        for subArgInfo in self.args[partIdx]['info']:
                            # update the relative indices of the argument's parts to those of the full string:
                            updatedSubArgInfo = dict(subArgInfo)
                            updatedSubArgInfo['indices'] = map(lambda x: x+strIndex, updatedSubArgInfo['indices'])
                            strInfo.append(updatedSubArgInfo)
                        # the index in the sentence increases by the number of words in the argument's substring:
                        strIndex += len(updatedSubArgInfo['indices'])
                    else:
                        strs.append(self.predicates[partIdx]['str'])
                        # a predicate word index is added to the list of the predicate indices:
                        strInfo[0]['indices'].append(strIndex)
                        strIndex += 1

                # put the concept expansion of the main predicate of the sentence:
                mainPredicateConceptStrs = okrData.getConceptStrings(self.parentPropId)
                mainPredicateConceptStrs = Utils.reduceSimilarWords(list(set(mainPredicateConceptStrs)))
                predStr = self.getPredicateBasicStr()
                if predStr in mainPredicateConceptStrs:
                    mainPredicateConceptStrs.remove(predStr) # remove the predicate value itself from the expansion
                if 'IMPLICIT' in mainPredicateConceptStrs:
                    mainPredicateConceptStrs.remove('IMPLICIT')  # remove the IMPLICIT string in case its their
                if len(mainPredicateConceptStrs) > 0:
                    strInfo[0]['expansion'] = mainPredicateConceptStrs

            else:  # implicit propositions, just put the args
                #strs.append('IMPLICIT')
                for argInfo in self.args:
                    #strs.append('[' + argInfo['str'] + ']')
                    strs.append(argInfo['str'])

                    # extend the information about the words in the substring of the argument:
                    for subArgInfo in argInfo['info']:
                        # update the relative indices of the argument's parts to those of the full string:
                        updatedSubArgInfo = dict(subArgInfo)
                        updatedSubArgInfo['indices'] = map(lambda x: x + strIndex, updatedSubArgInfo['indices'])
                        strInfo.append(updatedSubArgInfo)
                    # the index in the sentence increases by the number of words in the argument's substring:
                    strIndex += len(updatedSubArgInfo['indices'])


            self.str_full[tweetIdToUse] = ' '.join(strs)
            self.str_full_info[tweetIdToUse] = strInfo

        return self.str_full[tweetIdToUse], self.str_full_info[tweetIdToUse]

    def getCleanPredicateStr(self):
        # create the predicate string:
        predWords = self.getPredicateWordsNonStopWords()
        pred = ' '.join(predWords)

        # create the info object for the predicate:
        info = {'conceptId': self.parentPropId, 'indices': range(0, len(predWords))}

        # get all the other mention strings used for this predicate for the concept expansion:
        predicateConceptStrs = okrData.getConceptStrings(self.parentPropId)
        predicateConceptStrs = Utils.reduceSimilarWords(list(set(predicateConceptStrs)))
        if pred in predicateConceptStrs:
            predicateConceptStrs.remove(pred)  # remove the predicate value itself from the expansion
        if len(predicateConceptStrs) > 0:
            info['expansion'] = predicateConceptStrs


        return pred, info

    def isConceptInArgSlot(self, argId, conceptId):
        argIdx = self.argsMap[argId]
        if conceptId in self.args[argIdx]['argObj'].conceptIDs:
            return True
        return False

    def getContextStrAroundArg(self, argId, conceptId):
        # find where in the template the argument is:
        centerIdx = -1
        argIdx = self.argsMap[argId]
        for partIdx, part in enumerate(self.parts):
            if part[0] == Template.ARG and part[1] == argIdx:
                centerIdx = partIdx
                break

        # get the parts in the template to use (in the arg's context):
        indicesToUse = []
        if centerIdx >= 0:
            if centerIdx == 0: # beginning of template
                indicesToUse = [0, 1]
            elif centerIdx == len(self.parts) - 1: # end of template
                indicesToUse = [centerIdx - 1, centerIdx]
            else: # in the middle somewhere in the template
                indicesToUse = [centerIdx - 1, centerIdx, centerIdx + 1]

        # build the string composed of the context parts:
        strsToUse = []
        for idx in indicesToUse:
            if idx < len(self.parts):
                if self.parts[idx][0] == Template.PRED:
                    predIdx = self.parts[idx][1]
                    strsToUse.append(self.predicates[predIdx]['str'])
                else:
                    argIdx = self.parts[idx][1]
                    conceptIdToUse, tweetIdsToUse = self.args[argIdx]['argObj'].getTweetIdsOfConcept(conceptId, True)
                    strToUse, _ = okrData.getRepresentingString(conceptIdToUse, tweetIdsToUse[0])
                    strsToUse.append(strToUse) #self.args[argIdx]['str']) # TODO: Is this good enough?

        return ' '.join(strsToUse)







class Proposition:
    def __init__(self, id, alias):
        self.id = id
        self.alias = alias
        self.timestamp = None
        self.attributor = None
        self.templates = [] # a list of Template objects
        self.arguments = {} # for each argID, keeps the Argument object
        self.conceptIdAsArgs = {} # for each conceptID used in the proposition, keeps a list of the arg slots it appears in (with repeating)
        self.argumentTemplates = {}  # for each arg, a list of the templates that contain it (by index in the templates list)
        self.argumentsPrepositionsBefore = {} # for each arg, keeps a prepositions counters dictionary of words before it throughout the templates
        self.allPredicatesUsedCounters_nonStop = {} # keep all the non-stop-word words used as predictaes throughout the templates (keys) with counters (values)
        self.allPredicatesUsedCountersStems_nonStop = {}  # keep all the non-stop-word words used as predictaes throughout the templates as stems (keys) with counters (values)
        self.allPredicatesUsedCounters_stop = {}  # keep all the stop-words used as predictaes throughout the templates (keys) with counters (values)

        self.representingTemplateIdx = -1
        self.representingRemainingArgs = []

    def setProperties(self, timestamp, attributor):
        self.timestamp = timestamp
        self.attributor = attributor

    def addTemplate(self, templateStr, tweetsList):
        self.templates.append(Template(self.id, templateStr, tweetsList))

    def addArgument(self, argId, argDescription):
        # There are cases (incorrect ones) that an argument is input twice, and overwritten. This condition prevents it.
        if not argId in self.arguments:
            self.arguments[argId] = Argument(self.id, argId, argDescription)
            self.argumentTemplates[argId] = []

    def addArgumentMention(self, argId, conceptId, tweetsList):
        self.arguments[argId].addArgMention(conceptId, tweetsList)

        # count up the conceptID being used:
        if not conceptId in self.conceptIdAsArgs:
            self.conceptIdAsArgs[conceptId] = []
        self.conceptIdAsArgs[conceptId].append(argId)

    def setArgumentsInTemplates(self):
        for argId, argObj in self.arguments.iteritems():
            for templateIdx, template in enumerate(self.templates):
                if template.hasArgument(argId):
                    template.setArgument(argId, argObj)
                    self.argumentTemplates[argId].append(templateIdx)

    def countPrepositionsBeforeArgs(self):
        # for each argument keep counters of each preposition before it:
        for template in self.templates:
            argsPreds = template.getPrepositionBeforeArgs()
            for argId, predBeforeArg in argsPreds.iteritems():
                if not argId in self.argumentsPrepositionsBefore:
                    self.argumentsPrepositionsBefore[argId] = {}
                if not predBeforeArg in self.argumentsPrepositionsBefore[argId]:
                    self.argumentsPrepositionsBefore[argId][predBeforeArg] = 0
                self.argumentsPrepositionsBefore[argId][predBeforeArg] += 1

    def setAllPredicatesUsed(self):
        for template in self.templates:
            predWordsList = template.getPredicateWordsNonStopWords()
            for predWord in predWordsList:
                self.allPredicatesUsedCounters_nonStop[predWord] = self.allPredicatesUsedCounters_nonStop.get(predWord, 0) + 1

                predWordStem = stem(predWord)
                self.allPredicatesUsedCountersStems_nonStop[predWordStem] = self.allPredicatesUsedCountersStems_nonStop.get(predWordStem, 0) + 1

            preWordsStopsList = template.getPredicateWordsStopWords()
            for stopWord in preWordsStopsList:
                self.allPredicatesUsedCounters_stop[stopWord] = self.allPredicatesUsedCounters_stop.get(stopWord, 0) + 1

    def setRepresentingTemplate(self, templateIdx, remainingArgs):
        self.representingTemplateIdx = templateIdx
        self.representingRemainingArgs = remainingArgs

    def getRepresentativeMention(self, tweetId):
        for template in self.templates:
            if tweetId in template.tweetsList:
                # Found a template to use.
                # If the frequency of this proposition as an argument is more than once, just write out a predicate representation.
                if okrData.frequencyOfConceptAsArgument(self.id) > 1:
                    predStr, predInfo = template.getCleanPredicateStr()
                    return predStr, [predInfo]
                # otherwise use the full template string (including nesting):
                else:
                    return template.getFullStr(tweetId)
        return None, None

    def getKeywordRepresentation(self):
        return self.templates[0].getCleanPredicateStr()[0]

    def getRepresentingTemplateStr(self):
        if self.representingTemplateIdx > -1:
            # put that template as the main string:
            megaTemplateStr, megaTemplateStrInfo = self.templates[self.representingTemplateIdx].getFullStr()

            ## add the remaining arguments at the end of the string in parentheses:
            #argsStrs = self.getRemainingArgsStringAdditions()
            #if len(argsStrs) > 0:
            #    megaTemplateStr += ' (' + ', '.join(argsStrs) + ')'

            return megaTemplateStr, megaTemplateStrInfo
        else:
            return str([str(template) for template in self.templates]), None

    def getRemainingArgsStringAdditions(self):
        # add the remaining arguments at the end of the string in parentheses:
        argsStrs = []
        for remainingArg in self.representingRemainingArgs:
            argReprConceptId, argReprTweetId = self.arguments[remainingArg].getMostCommonConceptId()
            # argReprStr = okrData.getRepresentingString(argReprConceptId, argReprTweetId)
            # argStr = '[' + argReprStr + ']'
            ## if there's a preposition before the arg sometimes, put it with the arg in the string:
            # prepositionBeforeArg = self.getPrepositionBeforeArg(remainingArg)
            # if prepositionBeforeArg != None:
            #    argStr = prepositionBeforeArg + ' ' + argStr
            # argsStrs.append(argStr)

            argStr = self.getSentenceExpansionStr(argReprConceptId, remainingArg)
            argsStrs.append(argStr)

        return argsStrs

    def getPrepositionBeforeArg(self, argId):
        # return the preposition that is most frequent (if there is one at all):
        preposition = None
        if argId in self.argumentsPrepositionsBefore:
            preposition = max(self.argumentsPrepositionsBefore[argId].iteritems(), key=operator.itemgetter(1))[0]
        return preposition

    def getAllPredicateStemsNonStopWords(self):
        return self.allPredicatesUsedCountersStems_nonStop

    def getAllPredicateStopWords(self):
        return self.allPredicatesUsedCounters_stop

    def getConceptIdsAsArgs(self):
        return self.conceptIdAsArgs

    def getSentenceExpansionStr(self, conceptId, argId):
        '''
        Get a string with context around the argument specified with the conceptId used.
        :param argId: The argument for which to build a string around.
        :param conceptId: The concept to use in the argument slot.
        :return: A string built around the argument specified, with context.
        '''
        strRet = ''
        for templateIdx in self.argumentTemplates[argId]:
            if self.templates[templateIdx].isConceptInArgSlot(argId, conceptId):
                strRet = self.templates[templateIdx].getContextStrAroundArg(argId, conceptId)
                strRet = strRet.replace('IMPLICIT', '') # remove the word IMPLICIT from the string
                strRet = strRet.strip(',. |:;') # strip of unneeded characters
        return strRet

    def getConceptStrings(self):
        templateStrs = []
        for template in self.templates:
            templateStrs.append(template.getPredicateBasicStr())
        return templateStrs

    def getConceptExpansionStrs(self):
        '''
        For each argument in the proposition, returns a list of strings for the concept expansion.
        :return: Dictionary of key:argId, value:list of strings. And dictionary of key:argId. value:list of concepts.
        '''
        conceptExpansionDict = {}
        argToConceptIds = {}
        for argId, argObj in self.arguments.iteritems():
            argStrs, concepts = argObj.getConceptExpansionStrs()
            argStrs = Utils.reduceSimilarWords(list(set(argStrs))) # get a reduced list from the unique list of concepts
            if 'IMPLICIT' in argStrs:
                argStrs.remove('IMPLICIT')
            conceptExpansionDict[argId] = argStrs
            argToConceptIds[argId] = concepts

        return conceptExpansionDict, argToConceptIds

    def getFullTweetsList(self):
        allTweetIds = []
        for template in self.templates:
            allTweetIds.extend(template.tweetsList)
        return list(set(allTweetIds)) # only unique






class Entity:
    def __init__(self, id, alias):
        self.id = id
        self.alias = alias
        self.mentionCounters = {} # TODO: this will need to hold a list of tweet IDs instead of just a counter
        self.representativeMention = None
        # The information about the representing mention. The indices are just 0->length of representativeMention.
        # The conceptId, is just the ID of this entity.
        self.representativeMentionInfo = {'indices':[], 'conceptId':id}

    def addMention(self, mentionStr, mentionCount=1):
        if not mentionStr in self.mentionCounters:
            self.mentionCounters[mentionStr] = 0
        self.mentionCounters[mentionStr] += mentionCount

    def getRepresentativeMention(self, tweetId):
        # TODO: return the concept used in the specified tweetID (currently source tweets not avaialable for entity mentions)

        if self.representativeMention == None:
            self.representativeMention = max(self.mentionCounters.iteritems(), key=operator.itemgetter(1))[0]
            self.representativeMentionInfo['indices'] = range(0, len(self.representativeMention.split()))
        return self.representativeMention, self.representativeMentionInfo

    def getConceptStrings(self):
        return self.mentionCounters.keys()

    def getKeywordRepresentation(self):
        return max(self.mentionCounters.iteritems(), key=operator.itemgetter(1))[0]

    def getNumberOfMentions(self):
        return sum(self.mentionCounters.values())


class Tweet:
    def __init__(self, tweetId, tweetText):
        self.id = tweetId
        self.text = tweetText
        self.timestamp = None
        self.author = None
        self.authorId = None
    def __str__(self):
        return '{}_{}_{}_{}'.format(self.id, self.timestamp, self.author, self.text)

class Okr:

    def __init__(self, name):
        self.name = name
        self.propositionIDs = [] # the list of proposition IDs to use (non-filtered ones)
        self.propositions = {}
        self.filteredPropositions = [] # a list of {'propId':propId, 'reason':reasonStr} for all the propositions that are not to be used
        self.entities = {}
        self.conceptsAsArguments = {} # all locations where each concept is used as an argument (key:conceptID value:<list of {'propId':<>,'argId':<>}>)
        self.tweets = {}

    def addTweet(self, tweetId, tweetText):#timestamp, authorName, authorId):
        self.tweets[tweetId] = Tweet(tweetId, tweetText)

    def updateTweetMetadata(self, tweetId, timestamp, authorName, authorId):
        self.tweets[tweetId].timestamp = timestamp
        self.tweets[tweetId].author = authorName
        self.tweets[tweetId].authorId = authorId

    def addEntity(self, entityId, entityAlias):
        self.entities[entityId] = Entity(entityId, entityAlias)

    def addEntityMention(self, entityId, mentionStr, mentionCount):
        self.entities[entityId].addMention(mentionStr, mentionCount)

    def addProposition(self, propId, alias):
        self.propositions[propId] = Proposition(propId, alias)
        self.propositionIDs.append(propId)

    def setPropositionProperties(self, propId, timestamp, attributor):
        self.propositions[propId].setProperties(timestamp, attributor)

    def addPropositionTemplate(self, propId, templateStr, tweetsList):
        self.propositions[propId].addTemplate(templateStr, tweetsList)
        
    def addPropositionArgument(self, propId, argId, argDescription):
        self.propositions[propId].addArgument(argId, argDescription)
        
    def addPropositionArgumentMention(self, propId, argId, conceptId, tweetsList):
        self.propositions[propId].addArgumentMention(argId, conceptId, tweetsList)
        
        # keep the concept ID use:
        if not conceptId in self.conceptsAsArguments:
            self.conceptsAsArguments[conceptId] = []
        self.conceptsAsArguments[conceptId].append({'propId':propId,'argId':argId})
        
    def filterProposition(self, propId, reasonId):
        self.filteredPropositions.append({'propId':propId, 'reason':reasonId})
        if propId in self.propositionIDs:
            self.propositionIDs.remove(propId)

    def getRepresentingString(self, conceptId, tweetId):
        '''
        Gets the representing string and info of the concept specified in the tweet specified.
        :param conceptId:
        :param tweetId:
        :return: A string, and a list of dictionaries with the info about the parts of the string returned.
        '''

        if conceptId[0] == 'E':
            entityStr, entityStrInfo = self.entities[conceptId].getRepresentativeMention(tweetId)
            return entityStr, [entityStrInfo]
        else:
            return self.propositions[conceptId].getRepresentativeMention(tweetId)

    def getKeywordRepresentation(self, conceptId):
        if conceptId[0] == 'E':
            return self.entities[conceptId].getKeywordRepresentation()
        else:
            return self.propositions[conceptId].getKeywordRepresentation()

    def getConceptStrings(self, conceptId):
        if conceptId[0] == 'E':
            return self.entities[conceptId].getConceptStrings()
        else:
            return self.propositions[conceptId].getConceptStrings()

    def getEntityIdFromAlias(self, entityAlias):
        for entId, entInfo in self.entities.iteritems():
            if entInfo.alias == entityAlias:
                return entId
        return None

    def frequencyOfConceptAsArgument(self, conceptId, getList=False):
        if not conceptId in self.conceptsAsArguments:
            listOfProps = []
        else:
            listOfProps = [conceptInfo['propId'] for conceptInfo in self.conceptsAsArguments[conceptId]]

        if getList:
            return len(listOfProps), listOfProps
        else:
            return len(listOfProps)

    def preparePropositions(self):
        for proposition in self.propositions.values():
            proposition.setArgumentsInTemplates()
            proposition.countPrepositionsBeforeArgs()
            proposition.setAllPredicatesUsed()

    def prepareData(self):
        '''
        Preprocessing on the data.
        :return:
        '''
        self.preparePropositions()
        IntraPropositionMerge.intraPropositionMerge(okrData)

    def getMissingConceptsStrs(self, usedPropId, otherPropIdsList):
        '''
        Gets strings with the concepts in the propositions in otherPropIdsList that are not in proposition usedPropId.
        The string has the concept with some context around it.
        :param usedPropId: The proposition ID that is used.
        :param otherPropIdsList: The proposition IDs whose concept IDs should be accounted for (not im usedPropId).
        :return: A dictionary of key:conceptId, value:string
        '''

        # count up the concept IDs used throughout the cluster, not in the used proposition:
        conceptIdsLeft = {}
        for propId in otherPropIdsList:
            for conceptId in self.propositions[propId].conceptIdAsArgs:
                if not conceptId in self.propositions[usedPropId].conceptIdAsArgs:
                    if not conceptId in conceptIdsLeft:
                        conceptIdsLeft[conceptId] = []
                    conceptIdsLeft[conceptId].append(propId)

        # since we don't add the remaining args at the end of the gnerated sentence in parentheses
        # (commented out in getRepresentingTemplateStr calling getRemainingArgsStringAdditions), we add the
        # remaining arguments strings in the sentence expansion:
        for remainingArg in self.propositions[usedPropId].representingRemainingArgs:
            argReprConceptId, _ = self.propositions[usedPropId].arguments[remainingArg].getMostCommonConceptId()
            if not argReprConceptId in conceptIdsLeft:
                conceptIdsLeft[argReprConceptId] = []
            conceptIdsLeft[argReprConceptId].append(usedPropId)

        # for each missing concept, get a string that contains it with surrounding context:
        missingConceptsStrs = {}
        for conceptId in conceptIdsLeft:
            # just use the first proposition in out of otherPropIdsList that contains the concept:
            propIdSample = conceptIdsLeft[conceptId][0]
            # find the argument ID that holds the the concept in the chosen proposition:
            argId = -1
            for conceptInfo in self.conceptsAsArguments[conceptId]:
                if conceptInfo['propId'] == propIdSample:
                    argId = conceptInfo['argId']
                    break
            # get a context string for the concept in the chosen proposition:
            if argId > -1:
                missingConceptStr = okrData.propositions[propIdSample].getSentenceExpansionStr(conceptId, argId)
                missingConceptsStrs[conceptId] = missingConceptStr
            else:
                print 'ERROR: Could not find arg ID for concept ' + conceptId + ' in sentence expansion construction.'

        return missingConceptsStrs

    def getWordCloudList(self):
        '''
        Returns a list of pairs (keyword, score).
        :return:
        '''
        wordScores = []
        for entId, entInfo in self.entities.iteritems():
            keyword = entInfo.getKeywordRepresentation()
            keywordLower = keyword.lower()
            if not keywordLower in stopwords.words('english') and not keywordLower in Utils.PRONOUNS and len(keyword) > 1:
                wordScores.append((keyword, entInfo.getNumberOfMentions()))
        wordScores.sort(key=lambda tup: tup[1], reverse=True) # sort by the score
        return wordScores



okrData = None