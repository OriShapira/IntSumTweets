import operator


def intraPropositionMerge(okrData, printResults=False):
    for propId in okrData.propositionIDs:
        # get the approximated set cover of arguments using the templates of the proposition:
        templateIndicesToUse = _getTemplatesWithFullArgsCoverage(okrData, propId)
        _setRepresentingTemplateForProposition(okrData, propId, templateIndicesToUse)

        if printResults:
            print propId
            # the original templates of the current prop:
            for template in okrData.propositions[propId].templates:
                print '\t' + template.str_basic
            print '--'
            # the argument set cover templates:
            for templateIdx in templateIndicesToUse:
                print '\t' + okrData.propositions[propId].templates[templateIdx].str_basic
            print '--'
            # the representing template and remaining arguments:
            repIdx = okrData.propositions[propId].representingTemplateIdx
            repOtherArgs = okrData.propositions[propId].representingRemainingArgs
            print '\t' + okrData.propositions[propId].templates[repIdx].str_basic + '  ' + str(repOtherArgs)
            print '-' * 5

def _setRepresentingTemplateForProposition(okrData, propId, templateIndicesToUse):
    '''
    Set the template index of the representing template for the proposition, as well as the args
    not in use in the chosen tempate that are used in the proposition (in other templates).
    '''

    # NOTE: The method implemented in this function does not need the set cover method of finding
    #       the fewest templates covering all arguments. The method here would work also by just
    #       going over all templates in the proposition. So the following does the same:
    #           templatesToUse = range(len(m_propositions[propId]['templates'])) # just look at all templates

    remainingArgs = []

    if len(templateIndicesToUse) == 1:
        chosenTemplateIndex = templateIndicesToUse[0]
    else:
        # get the highest scoring template:
        templateScoresDict = _getTemplateScores(okrData, propId, templateIndicesToUse)
        highestScoringTemplateIndex = max(templateScoresDict.iteritems(), key=operator.itemgetter(1))[0]
        chosenTemplateIndex = highestScoringTemplateIndex

        # get the args in the proposition that are not in the chosen template:
        allArgsSet = set(okrData.propositions[propId].arguments.keys())  # the full set of args in the prop
        usedArgsSet = set(okrData.propositions[propId].templates[highestScoringTemplateIndex].argsMap.keys()) # the args in the best template
        remainingArgs = allArgsSet.difference(usedArgsSet) # the args not in the best template

    okrData.propositions[propId].setRepresentingTemplate(chosenTemplateIndex, remainingArgs)

def _getTemplateScores(okrData, propId, templateIdsToUse):
    # score each template by summing up the strength of its args (a more common arg is stronger)

    # first count up how many times each argument appears throughout the templates:
    argScores = {argId: len(listOfTemplatesWithArg) for argId, listOfTemplatesWithArg in okrData.propositions[propId].argumentTemplates.iteritems()}

    # score each template by summing up its argument scores:
    templateScores = {templateIdx: 0 for templateIdx in templateIdsToUse}
    for templateIdx in templateIdsToUse:
        for argId in okrData.propositions[propId].templates[templateIdx].argsMap:
            templateScores[templateIdx] += argScores[argId]

    return templateScores

def _getTemplatesWithFullArgsCoverage(okrData, propId):
    '''
    Gets a list of template indices for the proposition specified that covers all the arguments in the proposition.
    Implements an approximate set cover.
    :param okrData:
    :param propId: The ID of the proposition for which to get the set cover.
    :return: List of indices (in the proposition.templates list) that cover all the arguments in the specified proposition.
    '''
    allArgsSet = set(okrData.propositions[propId].arguments.keys())
    usedArgsSet = set()
    templateIndicesToUse = []

    # if there is just one template or this proposition only has an IMPLICIT predicate:
    if len(okrData.propositions[propId].templates) == 1 or okrData.propositions[propId].templates[0].isImplicit():
        return [0]  # just use the only template (first one)

    while len(allArgsSet) > 0:
        # find the template that has the most new arguments (uses the first one found if several are of the same size):
        maxIntersectionCount = -1
        maxIntersectionIdx = -1
        for templateIdx, templateInfo in enumerate(okrData.propositions[propId].templates):
            intersection = set.intersection(allArgsSet, templateInfo.argsMap.keys())
            if len(intersection) > maxIntersectionCount:
                maxIntersectionCount = len(intersection)
                maxIntersectionIdx = templateIdx

        # In rare occurrences, even though an argument is in the proposition's arguments dictionary, it isn't
        # used in any of the templates. In this case there will not be any intersection, and the count will be 0.
        # Once this occurs, we have covered all possible arguments, and we break the loop.
        if maxIntersectionCount <= 0:
            break

        # remove the argument ids just found:
        allArgsSet = allArgsSet.difference(okrData.propositions[propId].templates[maxIntersectionIdx].argsMap.keys())
        # add the argument ids found to the used args set:
        usedArgsSet.update(okrData.propositions[propId].templates[maxIntersectionIdx].argsMap.keys())
        # add the template found to the list to use:
        templateIndicesToUse.append(maxIntersectionIdx)

    return templateIndicesToUse


# def getFullTemplatesPerProposition(okrData):
#
#     allTemplateToUse = {}
#     megaTemplatePerProp = {}
#
#     for propId in okrData.propositions:
#         print propId
#         print len(okrData.propositions[propId].templates)
#         # print [predWord+' ; '+str(predInfo['count'])+' ; '+str(getAvgOfList(predInfo['locationsInTemplates'])) for predWord, predInfo in m_propositions[propId]['predicateWords'].iteritems()]
#         # print [str(argId)+' : '+argInfo['alias']+' ; '+str(argInfo['count'])+' ; '+str(getAvgOfList(argInfo['locationsInTemplates']))+' ; '+str(collections.Counter(argInfo['wordsBefore'])) for argId, argInfo in m_propositions[propId]['args'].iteritems()]
#         templates = [templateInfo.str_basic for templateInfo in okrData.propositions[propId].templates]
#         print '\n'.join(templates)
#         print '----'
#
#         # get the approximated set cover of arguments using the templates of the proposition:
#         templateIndicesToUse = _getTemplatesWithFullArgsCoverage(propId)
#         for templateIdx in templateIndicesToUse:
#             print okrData.propositions[propId].templates[templateIdx].str_basic
#
#         allTemplateToUse[propId] = templateIndicesToUse
#
#         _setRepresentingTemplateForProposition(okrData, propId, templateIndicesToUse)
#
#         print '=' * 20
#
#     # now that we have all the mega templates, put in nested proposition templates if relevant:
#     nestedPropositionHandling(megaTemplatePerProp)
#
#     # print 'Inserting nested: '
#     # argsCounters = countArgs(megaTemplatePerProp.keys())
#     # propIdsToRemove = []
#     # for propId in megaTemplatePerProp:
#     # for argId, argInfo in m_propositions[propId]['args'].iteritems():
#     # argAlias = argInfo['alias']
#     # if argAlias.startswith('*P') and argsCounters[argAlias] == 1:
#     # propIdOfNested = argAlias[1:] # P<num> the proposition that is to be replace by a template
#     # origMegaTemplate = megaTemplatePerProp[propId] # the template in which to replce the arg with a nested prop
#     # oldArgAlias = argAlias # the old arg alias to replace
#     # # get the template with which to replace the argument
#     # if propIdOfNested in megaTemplatePerProp:
#     # newNestedStr = megaTemplatePerProp[propIdOfNested]
#     # propIdsToRemove.append(propIdOfNested) # remove the proposition, since it is no longer a root proposition
#     # elif propIdOfNested in m_propositions:
#     # newNestedStr = m_propositions[propIdOfNested]['templatesFull'][0]
#     # elif propIdOfNested in m_propositionsRemoved:
#     # newNestedStr = m_propositionsRemoved[propIdOfNested]['templatesFull'][0]
#     # megaTemplatePerProp[propId] = replaceNestedPropArgWithTemplate(origMegaTemplate, oldArgAlias, newNestedStr)
#     # print propId + ': ' + megaTemplatePerProp[propId]
#     # # TODO: Need to do this recursivelly since there are nested inside nested
#
#     # for propId in propIdsToRemove:
#     # del(megaTemplatePerProp[propId])
#
#     return allTemplateToUse, megaTemplatePerProp