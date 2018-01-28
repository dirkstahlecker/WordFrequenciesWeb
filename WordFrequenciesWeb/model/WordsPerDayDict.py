import datetime
from WordDictBase import WordDictBase

class WordsPerDayDict(WordDictBase):
    #{ word : { 'count': count , 'lastOccurence': last occurence } } only counts one occurence per day

    def checkInvariants(self):
        pass

    #############################################
    #Constructors (and updaters)
    #############################################

    def addWord(self, word, count, lastOccurrence):
        if type(count) is not int:
            return False
        if type(lastOccurrence) is not datetime:
            return False

        self.internalDict[word] = {self.COUNT: count, self.LAST_OCCURRENCE: lastOccurrence}
        return self.checkInvariants()
