import datetime
from WordDictBase import WordDictBase

class WordDict(WordDictBase):
    #{ word : { 'count': count , 'lastDate': last occurence , 'firstDate': first occurence , 'wasUpper': started with uppercase letter } }

    def checkInvariants(self):
        pass

    #############################################
    #Constructors (and updaters)
    #############################################

    #Add a new word to the dictionary, or if the word exists already, replace its fields with the supplied new values
    #returns True if added successfully and False if not
    def addOrReplaceWord(self, word, count, lastOccurrence, firstOccurrence, wasUpper):
        if type(count) is not int:
            return False
        if type(lastOccurrence) is not datetime.datetime:
            return False
        if type(firstOccurrence) is not datetime.datetime:
            return False
        if type(wasUpper) is not bool:
            return False

        self.internalDict[word] = {self.COUNT: count, self.LAST_OCCURRENCE: lastOccurrence, self.FIRST_OCCURRENCE: firstOccurrence, self.WAS_UPPER: wasUpper}
        return self.checkInvariants()

    #TODO: figure out the difference between these two methods - they seem identical

    #Adds a new word to the dictionary. If it already exists, return False and do nothing
    def addWord(self, word, count, lastOccurrence, firstOccurrence, wasUpper):
        if word in self.internalDict:
            return False
        if type(count) is not int:
            return False
        if type(lastOccurrence) is not datetime.datetime:
            return False
        if type(firstOccurrence) is not datetime.datetime:
            return False
        if type(wasUpper) is not bool:
            return False

        self.internalDict[word] = {self.COUNT: count, self.LAST_OCCURRENCE: lastOccurrence, self.FIRST_OCCURRENCE: firstOccurrence, self.WAS_UPPER: wasUpper}
        return self.checkInvariants()

    #For every input that is not None, replace the specified word's value with that value
    def updateWord(self, word, count, lastOccurrence, firstOccurrence, wasUpper):
        if word not in self.internalDict:
            raise Exception(word + ' does not exist.')
        if count != None:
            self.setCount(word, count)
        if lastOccurrence != None:
            self.setLastOccurrence(word, lastOccurrence)
        if firstOccurrence != None:
            self.setFirstOccurrence(word, firstOccurrence)
        if wasUpper != None:
            self.setWasUpper(word, wasUpper)

    #############################################
    #Public getters
    #############################################

    def getFirstOccurrence(self, word):
        if self.exists(word):
            return self.internalDict[word][self.FIRST_OCCURRENCE]
        else:
            raise Exception(word + ' does not exist.')

    #############################################
    #Private setters
    #############################################

    def setCount(self, word, newCount):
        if newCount is not int:
            raise Exception('Count must be set to an integer')
        if self.exists(word):
            self.internalDict[word][self.COUNT] = newCount
        else:
            raise Exception(word + ' does not exist.')

    def setLastOccurrence(self, word, newDate):
        if newDate is not datetime.datetime:
            raise Exception('Last date must be set to a datetime.datetime')
        if self.exists(word):
            self.internalDict[word][self.LAST_DATE] = newDate
        else:
            raise Exception(word + ' does not exist.')

    def setFirstOccurrence(self, word, newDate):
        if newDate is not datetime.datetime:
            raise Exception('First date must be set to a datetime.datetime')
        if self.exists(word):
            self.internalDict[word][self.FIRST_DATE] = newDate
        else:
            raise Exception(word + ' does not exist.')

    def setWasUpper(self, word, wasUpper):
        if newDate is not bool:
            raise Exception('Was upper must be set to a boolean')
        if self.exists(word):
            self.internalDict[word][self.WAS_UPPER] = wasUpper
        else:
            raise Exception(word + ' does not exist.')    

 

