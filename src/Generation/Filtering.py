

def filterProps(okrData):
    filterer = FilterProps(okrData)
    filterer.doFilter()

class FilterProps:

    def __init__(self, okrData):
        self.okrData = okrData

        self.PRINT_STATS = False
        self.FILTERS = {
            # filter propositions that are implicit only:
            'Implicit': {'func':self.removeImplicitPropositions, 'showFiltered':False, 'dontRemoveIfArgUnique':True},
            # filter propositions that have no arguments:
            'No Arguments': {'func':self.removeNoArgPropositions, 'showFiltered':False, 'dontRemoveIfArgUnique':True},
            # filter propositions that have one argument only:
            'One Argument': {'func':self.removeOneArgPropositions, 'showFiltered':False, 'dontRemoveIfArgUnique':True},
            # filter attribution propositions:
            'Attribution': {'func':self.removeAttributionPropositions, 'showFiltered':False, 'dontRemoveIfArgUnique':False},
            # filter propositions that only have prepositions as predicate words:
            'Prepositions Only': {'func':self.removePrepositionPropositions, 'showFiltered':False, 'dontRemoveIfArgUnique':True},
            # filter propositions that only have stop words as predicate words:
            #'Stop Words': {'func':self.removeStopWordPropositions, 'showFiltered':False, 'dontRemoveIfArgUnique':False}
            # Filter propositions that are only used once as a nested proposition. If the proposition that it is used in
            #  was already filtered, then it is not filtered. For this reason, this filter is placed last:
            'Nested Once': {'func': self.removeSingleNestedPropositions, 'showFiltered': False, 'dontRemoveIfArgUnique': False},
        }
        # TODO: maybe try to filter out propositions that have predicates only at the extremities.

    def doFilter(self):
        for filterName, filterInfo in self.FILTERS.iteritems():
            # get the filter information:
            filterFunc = filterInfo['func']
            showFiltered = filterInfo['showFiltered']
            dontRemoveIfArgUnique = filterInfo['dontRemoveIfArgUnique']

            # filter out and get the prop IDs that were filtered:
            filteredPropositionsList = filterFunc(showFiltered=showFiltered, dontRemoveIfArgUnique=dontRemoveIfArgUnique)

            # mark them as filtered:
            for propId in filteredPropositionsList:
                self.okrData.filterProposition(propId, filterName)

            if self.PRINT_STATS:
                print 'Filter for ' + filterName + ' Propositions: ' + str(len(filteredPropositionsList))


    def _isImplicit(self, propId):
        # if all of the templates of the proposition are implicit predicates, return True:
        for template in self.okrData.propositions[propId].templates:
            if not template.isImplicit():
                return False
        return True  # all templates are an implicit proposition

    def _hasNoArgs(self, propId):
        return len(self.okrData.propositions[propId].arguments) == 0

    def _hasOneArg(self, propId):
        return len(self.okrData.propositions[propId].arguments) == 1

    def _isStopWordOnlyProp(self, propId):
        # if at least one of the templates of the proposition has a non-stopWord string, it is not a stop-word only prop:
        for template in self.okrData.propositions[propId].templates:
            if not template.isStopWordsOnly():
                return False
        return True  # all templates have only stop words as predicate words

    def _isSingleNestedProp(self, propId):
        # if the proposition is an argument exactly once, and the proposition in which it is used is not filtered:
        propAsArgCount, propAsArgPropositionIds = self.okrData.frequencyOfConceptAsArgument(propId, getList=True)
        if propAsArgCount == 1 and propAsArgPropositionIds[0] in self.okrData.propositionIDs:
            return True
        return False

    def _isAttribution(self, propId):
        # if at least one of the templates of the proposition is a non-attributor, it is not an attribution prop:
        for template in self.okrData.propositions[propId].templates:
            if not template.isAttrubution():
                return False
        return True  # all templates have are attributions

    def _isPrepositionOnlyProp(self, propId):
        # if at least one of the templates of the proposition has non-preposition words, it is not an attribution prop:
        for template in self.okrData.propositions[propId].templates:
            if not template.isPrepostionsOnly():
                return False
        return True  # all templates have all prepostion words


    def removeAttributionPropositions(self, showFiltered=False, dontRemoveIfArgUnique=False):
        '''
        Removes the propositions that are attributions, and returns the number of propositions filtered out.
        '''
        return self.removePropositions(self._isAttribution, printRemovedProp=showFiltered,
                                  verifyArgsExistsElsewhere=dontRemoveIfArgUnique)


    def removePrepositionPropositions(self, showFiltered=False, dontRemoveIfArgUnique=False):
        '''
        Removes the propositions that all of its templates have preposition predicates only,
        and returns the number of propositions filtered out.
        '''
        return self.removePropositions(self._isPrepositionOnlyProp, printRemovedProp=showFiltered,
                                  verifyArgsExistsElsewhere=dontRemoveIfArgUnique)


    def removeImplicitPropositions(self, showFiltered=False, dontRemoveIfArgUnique=False):
        '''
        Removes the propositions that all of its templates are implicit predicates and returns the number of propositions filtered out.
        '''
        return self.removePropositions(self._isImplicit, printRemovedProp=showFiltered,
                                  verifyArgsExistsElsewhere=dontRemoveIfArgUnique)


    def removeNoArgPropositions(self, showFiltered=False, dontRemoveIfArgUnique=False):
        '''
        Removes the propositions that don't have any arguments and returns the number of propositions filtered out.
        '''
        return self.removePropositions(self._hasNoArgs, printRemovedProp=showFiltered, verifyArgsExistsElsewhere=dontRemoveIfArgUnique)


    def removeOneArgPropositions(self, showFiltered=False, dontRemoveIfArgUnique=False):
        '''
        Removes the propositions that have exactly one argument and returns the number of propositions filtered out.
        '''
        return self.removePropositions(self._hasOneArg, printRemovedProp=showFiltered, verifyArgsExistsElsewhere=dontRemoveIfArgUnique)


    def removeStopWordPropositions(self, showFiltered=False, dontRemoveIfArgUnique=False):
        '''
        Removes the propositions that have only stop words as predicates and returns the number of propositions filtered out.
        '''
        return self.removePropositions(self._isStopWordOnlyProp, printRemovedProp=showFiltered,
                                  verifyArgsExistsElsewhere=dontRemoveIfArgUnique)

    def removeSingleNestedPropositions(self, showFiltered=False, dontRemoveIfArgUnique=False):
        '''
        Removes the propositions that have only stop words as predicates and returns the number of propositions filtered out.
        '''
        return self.removePropositions(self._isSingleNestedProp, printRemovedProp=showFiltered,
                                       verifyArgsExistsElsewhere=dontRemoveIfArgUnique)

    def removePropositions(self, filterFunc, printRemovedProp=False, verifyArgsExistsElsewhere=False):
        '''
        Removes the propositions that pass the filter function given and returns the number of propositions filtered out.
        The filter function should receive a propId, and return true iff specified proposition should be removed.
        If printRemovedProp is True, the filtered out propositions will be printed.
        If verifyArgsExistsElsewhere is True, a filterable proposition will not be removed if it contains an argument that doesn't exist anywhere else.
        '''
        global m_propositionsRemoved

        propIdsToFilter = []
        for propId in self.okrData.propositions:
            if filterFunc(propId):
                # now make sure the proposition is allowed to be filtered:
                if not verifyArgsExistsElsewhere or self.argsExistElsewhere(propId):
                    propIdsToFilter.append(propId)
                    if printRemovedProp:
                        print propId + ': ' + str([str(template) for template in self.okrData.propositions[propId].templates])

        return propIdsToFilter


    def argsExistElsewhere(self, propId):
        allArgsExistElsewhere = True

        # check if all the args in the specified proposition are mentioned in some ohter propoisition:
        for conceptId in self.okrData.propositions[propId].conceptIdAsArgs:
            foundCurConcept = False

            # look for the current concept ID in the other propositions:
            for otherPropId in self.okrData.propositions:
                if otherPropId != propId:
                    if conceptId in self.okrData.propositions[otherPropId].conceptIdAsArgs:
                        foundCurConcept = True
                        break  # found the argument alias in another existing proposition
            if not foundCurConcept:
                allArgsExistElsewhere = False
                break

        return allArgsExistElsewhere