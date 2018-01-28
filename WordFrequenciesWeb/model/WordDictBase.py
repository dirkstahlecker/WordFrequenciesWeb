
class WordDictBase():
    internalDict = {}

    def __str__(self):
        outStr = '';
        for word in self.internalDict:
            outStr += word + ': ' + str(self.internalDict[word]) + '\n'
        return outStr

    def checkInvariants(self):
        pass

    COUNT = 'count'
    LAST_OCCURRENCE = 'lastOccurrence'
    FIRST_OCCURRENCE = 'firstOccurrence'
    WAS_UPPER = 'wasUpper'


    #check if a word exists in the dictionary
    def exists(self, word):
        try:
            self.internalDict[word]
            return True
        except:
            return False

    #############################################
    #Public getters
    #############################################

    def get(self, word):
        if not self.exists(word):
            return False
        return self.internalDict[word]

    def getNumberOfWords(self):
        return len(self.internalDict)

    #returns None if not added successfully
    def getCount(self, word):
        if self.exists(word):
            return self.internalDict[word][self.COUNT]
        else:
            raise Exception(word + ' does not exist.')

    def incrementCount(self, word):
        if not self.exists(word):
            raise Exception(word + ' does not exist.')
        self.internalDict[word][self.COUNT] = self.internalDict[word][self.COUNT] + 1
        return True

    def getLastOccurrence(self, word):
        if self.exists(word):
            return self.internalDict[word][self.LAST_OCCURRENCE]
        else:
            raise Exception(word + ' does not exist.')

    def getSortedDictByCount(self):
        return sorted(self.internalDict.items(), key=lambda x: x[1][self.COUNT])

