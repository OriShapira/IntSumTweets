import json
import ntpath
import os
import sys

import ClusterInter
import CreateOutput
import Data
import Filtering
import InputParser
import OrderSentences


def handleFile(inFormat, okrDataFilePath, outputFilepath, tweetsListFilePath=None, tweetsMetadataFilePath=None):

    print 'Processing: ' + okrDataFilePath

    # get the name of the event from the filename:
    eventName = ntpath.basename(okrDataFilePath).split('.')[0]

    # initialize the OKR object:
    Data.okrData = Data.Okr(eventName)

    # parse the input files to form the OKR object:
    InputParser.parseInput(inFormat, okrDataFilePath, Data.okrData, tweetsListFilePath=tweetsListFilePath, tweetsMetadataFilePath=tweetsMetadataFilePath)

    #print 'Num propositions given: ' + str(len(Data.okrData.propositions))

    # filter out propositions that aren't needed:
    Filtering.filterProps(Data.okrData)

    #print 'Num propositions after filter: ' + str(len(Data.okrData.propositionIDs))

    # cluster together similar propositions:
    propClusters, clusterRepresentatives = ClusterInter.getPropositionClusters(Data.okrData)

    # aggregate all the information about the generated sentences:
    sentencesInfo = {}
    for clusterIdx, cluster in enumerate(propClusters):
        clusterRepPropId = clusterRepresentatives[clusterIdx]
        clusterRepStr, clusterRepStrInfo = Data.okrData.propositions[clusterRepPropId].getRepresentingTemplateStr()
        sentenceExpansionStrs = Data.okrData.getMissingConceptsStrs(clusterRepPropId, cluster)

        conceptExpansions, argIdsToConceptIds = Data.okrData.propositions[clusterRepPropId].getConceptExpansionStrs()

        allTweetIds = []
        for propId in cluster:
            allTweetIds.extend(Data.okrData.propositions[propId].getFullTweetsList())
        allTweetIds = list(set(allTweetIds))

        sentencesInfo[clusterIdx] = {'sentence':clusterRepStr, 'sentenceInfo':clusterRepStrInfo, 'tweets':allTweetIds,
                                     'sentenceExpansion':sentenceExpansionStrs, 'conceptExpansions':conceptExpansions,
                                     'clusterPropIds':cluster, 'clusterRepPropId': clusterRepPropId}

    # order the sentences:
    orderInfo = OrderSentences.orderSentences(sentencesInfo, Data.okrData)

    wordCloudList = Data.okrData.getWordCloudList()

    # output the sentences:
    if outputFilepath.endswith('.out'):
        outputStr = CreateOutput.getFullOutputString(Data.okrData, orderInfo, sentencesInfo)
        #outputStr = CreateOutput.getSummaryOutputStr(Data.okrData, orderInfo, sentencesInfo)
    elif outputFilepath.endswith('.json'):
        outputStr = CreateOutput.createOutputJson(Data.okrData, orderInfo, sentencesInfo)

    if outputFilepath == None:
        print outputStr
        print wordCloudList
    else:
        with open(outputFilepath, 'w') as outF:
            outF.write(outputStr)
        with open(outputFilepath+'_wordCloud.json', 'w') as outF:
            keywordsDict = {ind:{'str':keyword, 'score':score} for ind, (keyword, score) in enumerate(wordCloudList)}
            jsonOutput = json.dumps(keywordsDict, indent=4)
            outF.write(jsonOutput)

    # TODO:
    #   Edit distance of predicates => if small, combine as conjunction
    #   If common arguments consecutivelly, combine proposition with conjunction on the predicate
    #   If there are two templates sharing all their arguments, combine eith conjunction
    #   In the end put them in order of average time (although there may be cases that the generated sentences are a combination of diferently times facts, there are mahy cases where the order makes a difference to the understanding of the event)



if __name__ == '__main__':
    if os.path.isdir(sys.argv[1]):
        inputFolder = sys.argv[1]
        if sys.argv[2] == '-new':
            tweetsMetadataFilePath = None
        else:
            tweetsMetadataFilePath = sys.argv[2]

        extensionStr = ''
        if sys.argv[3] == '-screen':
            outputPath = None
        elif sys.argv[3] == '-out':
            outputPath = sys.argv[4]
            extensionStr = 'out'
        elif sys.argv[3] == '-json':
            outputPath = sys.argv[4]
            extensionStr = 'json'

        numFilesProcessed = 0
        for filename in os.listdir(inputFolder):
            if filename.endswith('.in'):
                okrDataFilePath = os.path.join(inputFolder, filename)
                tweetsListFilePath = os.path.join(inputFolder, filename[:-2]+'sentences')
                outputFilePath = os.path.join(outputPath, filename[:-2]+extensionStr) if outputPath != None else None
                inputFormat = InputParser.INPUT_FORMAT_OLD
            elif filename.endswith('.in.json'):
                okrDataFilePath = os.path.join(inputFolder, filename)
                tweetsListFilePath = None
                outputFilePath = os.path.join(outputPath, filename[:-7] + extensionStr) if outputPath != None else None
                inputFormat = InputParser.INPUT_FORMAT_NEW
            else:
                continue

            handleFile(inputFormat, okrDataFilePath, outputFilePath, tweetsListFilePath, tweetsMetadataFilePath)
            numFilesProcessed += 1

        if numFilesProcessed == 0:
            print('No files found. Make sure your files have the extension ".in" or ".in.json".')

    else:
        okrDataFilePath = sys.argv[1] # the OKR data file
        tweetsListFilePath = sys.argv[2] # the tweets list of the OKR event of the first file
        tweetsMetadataFilePath = sys.argv[3] # the full file of all tweets
        if sys.argv[4] == '-screen':
            outputFilePath = None
        else:
            outputFilePath = sys.argv[4]
        handleFile(InputParser.INPUT_FORMAT_OLD, okrDataFilePath, outputFilePath, tweetsListFilePath, tweetsMetadataFilePath)

