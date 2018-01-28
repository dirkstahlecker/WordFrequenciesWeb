import argparse
import re
import regex
import os
import operator
import argparse
import matplotlib  
matplotlib.use('TkAgg') #necessary for virtualenv with python3 not installed as a system framework
import matplotlib.pyplot as plt
import datetime
from Helper import Helper
from Preferences import Preferences
from PrintHelper import PrintHelper
import locale
import hashlib
from WordDict import WordDict
from WordsPerDayDict import WordsPerDayDict
from enum import Enum
from WordClass import WordClass

#Enum to carry the different settings for printing
class PrintOption(Enum):
    HIGHEST = 1
    LOOKUP = 2
    NAMES = 3
    RELATED = 4
    GRAPH = 5
    GRAPHENTRIES = 6
    WORDSPERDAY = 7
    NAMESPERDAY = 8
    ADDNAME = 9
    OPTION = 10
    LENGTH = 11
    GRAPHLENGTH = 12
    OVERALL = 13
    EXIT = 14

#Enum to carry the different commands the user can type
class CommandOptions(Enum):
    HIGHEST = 'highest'
    WPD = 'wpd'
    LOOKUP = 'lookup'
    NAMES = 'names'
    RELATED = 'related'
    NPD = 'npd'
    GRAPH = 'graph'
    GRAPH_ENTRIES = 'graphentries'
    GRAPH_LENGTH = 'graphlength'
    ADDNAME = 'addname'
    OPTION = 'option'
    LENGTH = 'length'
    OVERALL = 'overall'
    EXIT = 'exit'

class WordFrequencies:
###############################################################################################
# Members
###############################################################################################
    namesSet = set()
    wordDict = WordDict()
    namesDict = {} #{ name : ( count , last occurence ) }
    # wordsPerDayDict = {} #{ word : { 'count': count , 'lastOccurence': last occurence } } only counts one occurence per day
    wordsPerDayDict = WordsPerDayDict()
    namesPerDayDict = {} #{ word : ( count , last occurence ) }
    namesToGraphDict = {} #{ word : [ [ date , count ] ] }
    namesToGraphDictUniqueOccurences = {} #{ word : [ date ] }
    wordCountOfEntriesDict = {} #{ date : word count }
    relatedNamesDict = {} #{ name : { name : unique day count } }
    lastNamesForFirstNameDict = {} #{ first name : [ last names ] }
    totalNumberOfWords = 0
    dayEntryHashTable = {} #{ date : hash }

    firstDate = datetime.datetime(datetime.MAXYEAR,12,31)
    mostRecentDate = datetime.datetime(datetime.MINYEAR,1,1)

    namesURL = os.path.dirname(os.path.realpath(__file__)) + '/names.txt'
    prefs = Preferences() #stored the user's preferences for various things
    printer = PrintHelper(prefs)


###############################################################################################
# Loading and Setup
###############################################################################################    


###############################################################################################
# Data Processing
###############################################################################################
    #parse a line and add the words to the dictionaries
    #print the line to markunder file, with the proper qualification on names
    #all markunder printing should happen here
    def addLine(self, line, currentDate):
        # markunderFile = open(self.markUnderFilePath, 'a')

        words = line.split(' ')

        wordsToCount = 0 #used to calculate the length of entries - don't want to include invalid words in the word count TODO: rethink this?
        namesFound = set()
        for word in words:
            if word == '' or word == None or re.compile('^\s+$').search(word) != None:
                continue

            (beforeStuff, word, afterStuff) = Helper.cleanWordForInitialAdd(word)

            word = WordClass(word) #words are represented by the WordClass, which is basically an encapsulation of normal words and markup names in one object

            if self.prefs.COMBINE_PLURALS:
                if word.endswith("'s"):
                    word = WordClass.addWordOrMarkup(word.toString()[:len(word)-2]) #TODO: this is broken

            wasUpper = False;
            if word.toString()[:1].isupper():
                wasUpper = True;
            originalWord = word
            word = Helper.cleanWord(word) #this strips off all punctuation and other information that we want to pass into markup.

            if not Helper.valid(word):
                continue
            wordsToCount += 1

            #names
            if word in self.namesSet and (Preferences.REQUIRE_CAPS_FOR_NAMES and wasUpper):
                namesFound.add(word)

                try:
                    self.namesDict[word] = (self.namesDict[word][0] + 1, currentDate)
                except:
                    self.namesDict[word] = (1, currentDate)

                #names per day
                try:
                    if self.namesPerDayDict[word][1] != currentDate:
                        self.namesPerDayDict[word] = (self.namesPerDayDict[word][0] + 1, currentDate)
                except:
                    self.namesPerDayDict[word] = (1, currentDate)

                #names for graphing purposes
                try: #{ word : [ [ date , count ] ] }
                    self.namesToGraphDict[word] #trigger exception
                    if self.namesToGraphDict[word][-1][0] == currentDate: #increment count
                        self.namesToGraphDict[word][-1][1] += 1
                    else: #start a new tuple with a new date
                        self.namesToGraphDict[word].append([currentDate, 1])
                except: #this name hasn't been encountered yet
                    self.namesToGraphDict[word] = [[currentDate, 1]]

                #names for graph, counting on unique occurences
                try: #{ word : [ date ] }
                    self.namesToGraphDictUniqueOccurences[word].append(currentDate)
                except:
                    self.namesToGraphDictUniqueOccurences[word] = [currentDate]

            #words
            if self.wordDict.exists(word):
                self.wordDict.addOrReplaceWord(word, self.wordDict.getCount(word) + 1, currentDate, self.wordDict.getFirstOccurrence(word), wasUpper)
            else:
                self.wordDict.addWord(word, 1, currentDate, currentDate, wasUpper) #TODO: wasUpper wasn't there originally
            
            #words per day
            if self.wordsPerDayDict.exists(word):
                self.wordsPerDayDict.addWord(word, self.wordsPerDayDict.getCount(word), currentDate) #TODO: was addOrReplaceWord, need to think what it should be
            else:
                self.wordsPerDayDict(word, 1, currentDate)

            #TODO: this is being moved to its own class to be called separately
            # if self.prefs.DO_MARK_UNDER:
            #     #if it's a name, qualify it for the markunder
            #     if word in self.namesSet:# or not (Preferences.REQUIRE_CAPS_FOR_NAMES and wasUpper):
            #         markUnderWord = self.getMarkUnderWord(word, originalWord, line, currentDate)
            #     else:
            #         markUnderWord = word

            #     markunderFile.write(markUnderWord + ' ')

        # markunderFile.close()
        return (wordsToCount, namesFound)


###############################################################################################
# Graphing and Printing
###############################################################################################
    #print the x most occuring words
    #num: number to print. if 'all', prints all
    #TODO: it would be nice to move at least part of this function to the printer class
    def printHighest(self, args, option):
        if self.prefs.VERBOSE:
            print('args: ', end=' ')
            print(args)
            print('option: ', end=' ')
            print(option)

        if option == PrintOption.RELATED:
            nameForRelated = args[0]
            args = args[1:]
            if len(args) < 1:
                print('Too few arguments.')
                return
            if self.prefs.VERBOSE:
                print('nameForRelated: ' + nameForRelated)

        start_num = 0
        end_num = 0
        index1 = 0
        index2 = 1

        if len(args) == 1: #only an end num
            try:
                if (args[index1] == 'all'):
                    end_num = float('inf')
                else:
                    end_num = int(args[index1])
            except:
                print('Invalid arguments')
                return
        elif len(args) >= 2: #start and end
            try:
                start_num = int(args[index1])
                if (args[index2] == 'all'):
                    end_num = float('inf')
                else:
                    end_num = int(args[index2])
            except:
                print('Invalid arguments')
                return

        if self.prefs.VERBOSE:
            print('start_num: ', end=' ')
            print(start_num, end=' ')
            print(' end_num ', end=' ')
            print(end_num)

        #TODO: add headers to all cases
        if option == PrintOption.NAMES:
            sortedNamesDict = sorted(list(self.namesDict.items()), key=operator.itemgetter(1))
            sortedNamesDict.reverse()
            end_num = min(end_num, len(sortedNamesDict))
            self.printer.makePrettyHeader('Word', 'Count', 'Last Occurence')
            for x in range(start_num, end_num):
                self.printer.makeOutputPretty(sortedNamesDict[x])
        elif option == PrintOption.RELATED:
            #TODO: deal with 'all' here, since it won't be caught earlier
            sortedRelatedNamesDict = sorted(list(self.relatedNamesDict[nameForRelated].items()), key=operator.itemgetter(1))
            sortedRelatedNamesDict.reverse()
            print('Related names for ' + nameForRelated + ':\n')
            self.printer.makePrettyHeader('Name', 'Count')
            end_num = min(end_num, len(sortedRelatedNamesDict))
            for x in range(start_num, end_num):
                self.printer.makeOutputPrettyRelated(sortedRelatedNamesDict[x])
        elif option == PrintOption.WORDSPERDAY:
            sortedWordsPerDayDict = self.wordsPerDayDict.getSortedDictByCount()
            sortedWordsPerDayDict.reverse()
            end_num = min(end_num, len(sortedWordsPerDayDict))
            self.printer.makePrettyHeader('Word', 'Count', 'Last Occurence')
            for x in range(start_num, end_num):
                self.printer.makeOutputPrettyWPD(sortedWordsPerDayDict[x])
        elif option == PrintOption.NAMESPERDAY:
            sortedNamesPerDayDict = sorted(list(self.namesPerDayDict.items()), key=operator.itemgetter(1))
            sortedNamesPerDayDict.reverse()
            end_num = min(end_num, len(sortedNamesPerDayDict))
            self.printer.makePrettyHeader('Name', 'Count', 'Last Occurence')
            for x in range(start_num, end_num):
                self.printer.makeOutputPretty(sortedNamesPerDayDict[x])
        elif option == PrintOption.LENGTH:
            sortedLengthOfEntriesDict = sorted(list(self.wordCountOfEntriesDict.items()), key=operator.itemgetter(1))
            sortedLengthOfEntriesDict.reverse()
            end_num = min(end_num, len(sortedLengthOfEntriesDict))
            self.printer.makePrettyHeader('Date', 'Count')
            for x in range(start_num, end_num):
                self.printer.makeOutputPrettyLength(sortedLengthOfEntriesDict[x])
        else: #regular words
            self.printer.makePrettyHeader('Word', 'Count', 'Last Occurence')
            sortedWordsDict = self.wordDict.getSortedDictByCount()
            sortedWordsDict.reverse()
            end_num = min(end_num, len(sortedWordsDict))
            for x in range(start_num, end_num):
                self.printer.makeOutputPrettyWordsDict(sortedWordsDict[x])


    #graphs the number of occurences of the name per day
    def graphAnalytics(self, args):
        #{ word : [ [ date , count ] ] }
        name = args[0]
        try:
            self.namesToGraphDict[name]
        except:
            print('Invalid input - must be a valid name')
            return
        try:
            x = [date[0] for date in self.namesToGraphDict[name]]
            y = [count[1] for count in self.namesToGraphDict[name]]
            
            ax = plt.subplot(111)
            ax.bar(x, y, width=2)
            ax.xaxis_date()

            plt.show()
        except:
            print('Unknown error occured while graphing')

    #graphs a bar for each day that an entry exists
    def graphEntries(self, args):
        #{ date : word count }
        sortedLengthOfEntriesDict = sorted(list(self.wordCountOfEntriesDict.items()), key=operator.itemgetter(1))
        x = [i[0] for i in sortedLengthOfEntriesDict]
        y = [1 for j in sortedLengthOfEntriesDict]
        self.graphHelper(x, y)

    def graphHelper(self, x, y):
        ax = plt.subplot(111)
        ax.bar(x, y, width=2)
        ax.xaxis_date()
        plt.show()

    def graphNameValue(self, in_dict):
        x = list(in_dict.keys())
        y = list(in_dict.values())
        self.graphHelper(x, y)

    def lookupWord(self, args):
        word = args[0]
        if not self.wordDict.exists(word):
            print('Invalid word')
            return
        print(word + ': ')
        print('First usage: ' + str(self.wordDict.getFirstOccurrence(word)))
        print('Last usage: ' + str(self.wordDict.getLastOccurrence(word)))
        total_uses = self.wordDict.getCount(word)
        total_days_used = self.wordsPerDayDict.getCount(word)
        total_number_of_days = len(self.wordCountOfEntriesDict)
        print('Total usages: ' + str(total_uses))
        print('Total days with at least one usage: ' + str(total_days_used))
        length = (self.wordDict.getLastOccurrence(word) - self.wordDict.getFirstOccurrence(word)).days
        print('Length from first use to last: ' + Helper.daysAsPrettyLength(length))
        print('Average usages per day: ' + str(float(total_uses) / length))
        print('Percentage of days with at least one useage: ' + str(round(float(total_days_used) / total_number_of_days * 100, 2)) + '%')

    def overallAnalytics(self):
        print('Total number of entries: ', end=' ')
        print(len(self.wordCountOfEntriesDict))
        print('First entry: ', end=' ')
        print(Helper.prettyPrintDate(self.firstDate))
        print('Last entry: ', end=' ')
        print(Helper.prettyPrintDate(self.mostRecentDate))
        print('Total days from first to last entry: ', end=' ')
        totalDays = self.mostRecentDate - self.firstDate #this is correct
        days = totalDays.days
        print(days)
        print('Percentage of days from first to last with an entry: ', end=' ')
        print(str(round(float(len(self.wordCountOfEntriesDict)) / days * 100, 2)) + '%')
        print('Average length per entry: ', end=' ')
        numberOfEntries = len(self.wordCountOfEntriesDict)
        sumOfLengths = 0
        longestEntryLength = 0
        for date in list(self.wordCountOfEntriesDict.keys()):
            length = self.wordCountOfEntriesDict[date]
            if length > longestEntryLength:
                longestEntryLength = length
                longestEntryDate = date
            sumOfLengths += length 
        print(round(float(sumOfLengths) / numberOfEntries, 2))
        print('Longest entry: ' + str(longestEntryLength) + ' words on ', end=' ')
        print(Helper.prettyPrintDate(longestEntryDate))
        print('Total number of words written: ', end=' ')
        print(locale.format("%d", self.totalNumberOfWords, grouping=True))



###############################################################################################
# Names
###############################################################################################
    def addRelatedNames(self, namesFound):
        #{ name : { name : unique day count } }
        for keyName in namesFound:
            for otherName in namesFound:
                if keyName == otherName:
                    continue
                try:
                    self.relatedNamesDict[keyName]
                except:
                    self.relatedNamesDict[keyName] = {}
                try: 
                    self.relatedNamesDict[keyName][otherName] += 1
                except:
                    self.relatedNamesDict[keyName][otherName] = 1

    #populate namesList from file
    def makeNamesSet(self):
        try:
            f = open(self.namesURL, 'r') #TODO: error handling
        except:
            raise Exception("Names file not found")
        self.namesSet.clear()
        line = f.readline()
        while line != '':
            self.namesSet.add(line.strip().lower()) #TODO: does this do anything? What?
            line = f.readline()
        f.close()

    #iterate over 
    def guessNamesHelper(self, guessedNamesSet):
        newNames = set()
        print('Are these names? (y/n)')
        for name in guessedNamesSet:
            if name in self.namesSet:
                break
            inp = input(name + ': ')
            if inp == 'y':
                newNames.add(name.lower())

        f = open(self.namesURL, 'r+')
        for name in newNames:
            f.write(name + '\n')
        f.close()

    #try to guess what is a name by looking for capitalized letters in the middle of sentences
    def guessNames(self, line, testFlag = False):
        guessedNamesSet = set()
        names = regex.findall('[^\.]\s+([ABCDEFGHIJKLMNOPQRSTUVWXYZ][\w]+)\W', line, overlapped=True)

        try: 
            for name in names:
                if name.lower() not in self.namesSet:
                    guessedNamesSet.add(name)
        except:
            return

        #want to return the guessedNamesSet here if this is running for a test 
        #TODO: figure out how to send more input during a test and get rid of this hack
        if testFlag:
            return guessedNamesSet
        self.guessNamesHelper(guessedNamesSet)

    #Add a name manually to the names set
    def addName(self, args):
        name = args[0]
        if name in self.namesDict:
            print("Name already added")
            return
        self.namesSet.add(name);
        f = open(self.namesURL, 'a')
        f.write('\n' + name)
        f.close()

    def removeName(self, name):
        self.namesSet.remove(name);
        f = open(self.namesURL, 'r+')
        f.clear()
        for name in self.namesSet:
            f.write(name) + '\n'
        f.close()


###############################################################################################
# Control Loop
###############################################################################################
    def main(self, args):
        self.mainSetup(args)
        self.runMainLoop()

    #break apart the main function for testing
    def mainSetup(self, args):
        locale.setlocale(locale.LC_ALL, 'en_US')
        fileurl = args.file

        if args.verbosity:
            self.prefs.VERBOSE = True
        if args.combineplurals:
            self.prefs.COMBINE_PLURALS = True
        if args.guessnames:
            self.prefs.GUESS_NAMES = True
        if args.markunder:
            self.prefs.DO_MARK_UNDER = True
            print('Set DO_MARK_UNDER=True')
#        if args.noMarkunder:
#            self.prefs.DO_MARK_UNDER = False
#            print 'Set DO_MARK_UNDER=False'

        self.makeNamesSet()
        self.readFile(fileurl)

    def runMainLoop(self):
        # if self.prefs.GUESS_NAMES:
        #     self.getGuessedNames()
        while True:
            print('''
    Options:
    Highest x words             highest [num | all] (num | all)
    Highest x words per day     wpd [num | all]
    Lookup                      lookup [word]
    Highest x names             names [num | all]
    Related Names               related [name] [num | all]
    Highest x names per day     npd [num | all]
    Graph names                 graph [name]
    Graph entries               graphentries
    Graph length                graphlength
    Add name                    add name [name]
    Set Options                 option [option_name] [value]
    Length                      length [num | all]
    Overall analytics           overall
    Exit                        exit
    ''')
            if not self.parseInput(input('>')):
                return

    def parseInput(self, inpStr):
        parts = inpStr.split()
        command = parts[0].lower().strip().lstrip()
        args = parts[1:]
        if (self.prefs.VERBOSE):
            print('Parsed arguments: command: ' + str(command) + ' args: ' + str(args))
        return self.callInputFunction(command, args)

    def readFile(self, url):
        try:
            f = open(url, 'r')
        except:
            print('File not found')
            newPath = input('Enter new path > ');
            return self.readFile(newPath) #TODO: this doesn't work for entirely unknown reasons

        newdate = re.compile('\s*([0-9]{1,2}-[0-9]{1,2}-[0-9]{2})\s*')
        currentDateStr = None
        currentDateObj = None
        numWords = 0
        namesFound = set()
        totalWordNum = 0

        currentDayEntry = '' #holds all the lines for the current day, so we can compute a hash of the day later on
        
        line = f.readline()
        while (line != ''):
            if self.prefs.GUESS_NAMES:
                self.guessNames(line)
            #check a line to see if it's a date, therefore a new day
            dateFound = newdate.match(line)
            if dateFound != None: #it's a new date, so wrapup the previous date and set up to move onto the next one
                if namesFound != None:
                    self.addRelatedNames(namesFound)
                    namesFound = set()
                    self.dayEntryHashTable[currentDateObj] = hashlib.md5(currentDayEntry.encode()) #TODO: deal with first date

                if numWords > 0:
                    self.wordCountOfEntriesDict[currentDateObj] = numWords #should be here, since we want it triggered at the end
                totalWordNum += numWords
                numWords = 0
                currentDateStr = dateFound.group(0)
                currentDateStr = Helper.formatDateStringIntoCleanedString(currentDateStr)
                currentDateObj = Helper.makeDateObject(currentDateStr)

                if currentDateObj > self.mostRecentDate: #found a higher date than what we've seen so far
                    self.mostRecentDate = currentDateObj
                if currentDateObj < self.firstDate: #found a lower date than what we have now
                    self.firstDate = currentDateObj
                line = line[len(currentDateStr):] #remove date from line, so it's not a word

            if currentDateStr != None:
                (wordsFound, namesFoundThisLine) = self.addLine(line, currentDateObj)
                for name in namesFoundThisLine:
                    namesFound.add(name)
                numWords += wordsFound
            line = f.readline()
            currentDayEntry += line #add line to the day's entry

        #need to capture the last date for the entry length
        self.wordCountOfEntriesDict[currentDateObj] = numWords 
        self.totalNumberOfWords = totalWordNum + numWords #need to get words from last line
        f.close()

    #args is a list of arguments in order
    def callInputFunction(self, inp, args):
        if inp == CommandOptions.HIGHEST.value:
            self.printHighest(args, None)
        elif inp == CommandOptions.LOOKUP.value:
            self.lookupWord(args)
        elif inp == CommandOptions.NAMES.value:
            self.printHighest(args, PrintOption.NAMES)
        elif inp == CommandOptions.RELATED.value:
            self.printHighest(args, PrintOption.RELATED)
        elif inp == CommandOptions.GRAPH.value:
            self.graphAnalytics(args)
        elif inp == CommandOptions.GRAPH_ENTRIES.value:
            self.graphEntries(args)
        # elif inp == 'gpd':
        #     self.graphAnalyticsPerDay(args)
        elif inp == CommandOptions.WPD.value:
            self.printHighest(args, PrintOption.WORDSPERDAY)
        elif inp == CommandOptions.NPD.value:
            self.printHighest(args, PrintOption.NAMESPERDAY)
        elif inp == CommandOptions.ADDNAME.value:
            self.addName(args)
        elif inp == CommandOptions.OPTION.value:
            print("Setting options isn't supported yet")
            pass
        elif inp == CommandOptions.LENGTH.value:
            self.printHighest(args, PrintOption.LENGTH)
        elif inp == CommandOptions.GRAPH_LENGTH.value:
            self.graphNameValue(self.wordCountOfEntriesDict)
        elif inp == CommandOptions.OVERALL.value:
            self.overallAnalytics()
        elif inp == CommandOptions.EXIT.value:
            return False
        else:
            print('Unknown command.')
        return True





###############################################################################################
###############################################################################################
# Markup
###############################################################################################
###############################################################################################

#this is used for going through a pre-existing file, checking it for names, and converting them to markup.
#Existing markup is ignored, everything is preserved except for changing names into markup. Everything is
#written back to a different output file
class Markup():
    lastNamesForFirstNameDict = {} #{ first name : [ last names ] }
    namesURL = os.path.dirname(os.path.realpath(__file__)) + '/names.txt'
    namesSet = set()
    markUpFilePath = os.path.dirname(os.path.realpath(__file__)) + '/markup.txt'
    uniqueDisplayNamesToNameDict = {} # { display name : ( first name , last name ) } if specified to automatically assign a last name to a given first name, hold it here

    NUM_WORDS_TO_PRINT_BEFORE = 15
    NUM_WORDS_TO_PRINT_AFTER = 5

    def main(self, args):
        self.makeNamesSet()
        self.lookForWarningsAndAlert(args.file)
        self.readFile(args.file)

    #TODO: untested
    #Looks through the entire document and shows a warning if there are things that could cause a problem
    def lookForWarningsAndAlert(self, url):
        f = open(url, 'r')
        warnings = []
        if regex.search('[\S]+/[\S]+', f.read()) != None: #slashes should be split upon as separate words but aren't
            warnings.append('File contains words separated by a "/". Split the words apart with a space on either side of the "/"')

        if len(warnings) > 0:
            for warning in warnings:
                print(warning, end='\n')

    #populate namesList from file
    def makeNamesSet(self):
        try:
            f = open(self.namesURL, 'r') #TODO: error handling
        except:
            raise Exception("Names file not found")
        self.namesSet.clear()
        name = f.readline()
        while name != '':
            self.namesSet.add(name.strip().lower())
            name = f.readline()
        f.close()

    def readFile(self, url):
        try:
            f = open(url, 'r')
        except:
            print('File not found')
            newPath = input('Enter new path > ');
            return self.readFile(newPath) #TODO: this doesn't work for entirely unknown reasons

        markupFile = open(self.markUpFilePath, 'a')
        markupFile.write('\n\n\n')
        markupFile.close()
        allWords = []
        line = f.readline()
        # last20Words = [] #maintains the last 20 words to give the user context for the name, which is a rolling list of 20 words ending in the particular name of note
        while line != '':
            markupFile = open(self.markUpFilePath, 'a')
            words = line.split(' ')
            # last20Words = []
            for currentIndex in range(len(words) - 1):
                word_str = words[currentIndex]
                # if len(last20Words) >= 20:
                #     last20Words.pop(0)
                # last20Words.append(word_str)

                (word_beforeStuff, word_str, word_afterStuff) = Helper.cleanWordForInitialAdd(word_str)

                if Helper.cleanWord(word_str, stripApostropheS=True) in self.namesSet:
                    wasPluralWithApostrophe = False
                    word_str = word_str.translate(str.maketrans({'‘':"'",'’':"'"})) #need to change from smart quotes to regular
                    if word_str.endswith("'s"):
                        word_str = word_str[:-2]
                        wasPluralWithApostrophe = True
                    word_class = self.getMarkUnderWord(word_str, words, currentIndex, wasPluralWithApostrophe)
                else:
                    word_class = WordClass.addWordOrMarkup(word_str)
                allWords.append(word_class)
                markupFile.write(word_beforeStuff + word_class.printMarkup() + word_afterStuff + ' ') #need to manually add a space since they're removed in the split
                #TODO: add spaces back only where they were taken from
            markupFile.close()
            line = f.readline()


    #TODO: breaks on 'name1/name2' - need to split apart somehow

    #only called for names
    #ask which name it is, store it in a markup format, and compute a hash of the day
    #return either the word unchanged, or the markup name if it's a name
    #returns WordClass object
    def getMarkUnderWord(self, displayName, wordsList, currentIndexInWordsList, wasPluralWithApostrophe):
        assert type(displayName) is str
        originalWord = displayName #needed when the name isn't actually a name
        displayName = Helper.cleanWord(displayName, True)

        print('\n\n\n')
        # for x in last20Words:
        #     print(x + ' ', end='')
        for x in range(self.NUM_WORDS_TO_PRINT_BEFORE, 0, -1):
            # print(x)
            if x > currentIndexInWordsList: #if the name is less than NUM_WORDS_TO_PRINT_BEFORE words in, it will wrap around backwards, which we don't want
                continue
            print(wordsList[currentIndexInWordsList - x] + ' ', end='')
        print(displayName + ' ' , end='')
        for x in range(1, self.NUM_WORDS_TO_PRINT_AFTER):
            print(wordsList[currentIndexInWordsList + x] + ' ', end='')



        print('\n' + displayName + ':')
        numPossibleLastNames = 0

        if displayName in self.uniqueDisplayNamesToNameDict.keys(): #we've specified to give the same markup to all these display names
            firstName = self.uniqueDisplayNamesToNameDict[displayName][0]
            lastName = self.uniqueDisplayNamesToNameDict[displayName][1]
        else: #proceed normally
            firstName = ''
            print('Is this the proper first name for ' + displayName + '? [enter] for yes, [n] for no')
            isProperFirstName = input('>')
            if isProperFirstName == 'n':
                print('Enter proper first name (or enter "None" if this is not a name)')
                possibleFirstName = input('>')
                if possibleFirstName == 'None' or possibleFirstName == 'none': #not actually a name
                    return WordClass.addWordOrMarkup(originalWord)
                firstName = possibleFirstName
            else:
                firstName = displayName

            try:
                self.lastNamesForFirstNameDict[firstName] #trigger exception if there's one to be thrown
                for nameFromDict in self.lastNamesForFirstNameDict[firstName]:
                    print(str(numPossibleLastNames) + ': ' + nameFromDict)
                    numPossibleLastNames = numPossibleLastNames + 1
                print('Or type new last name (append "!" at end to auto assign all instance of this name to this last name):')
            except:
                print('Type last name (append "!" at end to auto assign all instance of this name to this last name):')

            #get the last name either from the number of the choice (if it's a number) or the last name that was directly entered
            lastName = ''
            choice = input('>')
            lastName = choice
            for x in range(0, numPossibleLastNames):
                if choice == str(x):
                    lastName = self.lastNamesForFirstNameDict[firstName][x]
                break

            if lastName[-1] == '!': #specify that all instance of this display name are assigned to this last name, without asking again
                lastName = lastName[:-1]
                self.uniqueDisplayNamesToNameDict[displayName] = (firstName, lastName)

        try:
            if lastName not in self.lastNamesForFirstNameDict[firstName]:
                self.lastNamesForFirstNameDict[firstName].append(lastName)
        except:
            self.lastNamesForFirstNameDict[firstName] = [lastName]

        return WordClass.addNameWithMarkupPieces(displayName, firstName, lastName, wasPluralWithApostrophe)


###############################################################################################
# Main 
###############################################################################################
#Options need to be set on startup
if __name__ == '__main__':
    wf = WordFrequencies()
    mu = Markup()

    #TODO: integrate this into the word frequencies class itself
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to file to examine')
    parser.add_argument('-v', '--verbosity', action='store_true', help='Enable verbose output')
    parser.add_argument('-p', '--combineplurals', action='store_true', help='Combine plurals')
    parser.add_argument('-g', '--guessnames', action='store_true', help='Guess names')
    parser.add_argument('-m', '--markunder', action='store_true', help='Enable markunder')
    parser.add_argument('-nm', '--noMarkunder', action='store_false', help='Disable markunder')
    args = parser.parse_args()

    if args.markunder:
        mu.main(args)
    else:
        wf.main(args)


'''
TODO: 
replace data structures with something more readable and maintainable (some sort of named nested tree maybe)

flag to ignore trailing s and then combine both "word" and "words" into same 

allow graphing for words and not just names

what names each name is frequently found with 
    refine to only look at names in the same paragraph maybe?

figure out how to deal with "[date] through [date]:"

use constants for strings

figure out what to do with multiple people of the same name
    maybe generate a mark under text file that shadows the journal with markup on the names for disambiguation
        this could also work toward caching
        maybe calculate a hash of the day after going through and generating the markdown then using that to see what has been updated

have a reverse order flag of some sort (allow to view in ascending order rather than descending)

allow option to filter by dates

connect this to other things
    step counter 
    google location
    texts sent/received
    pictures

make a gui navigable interface

noMarkUnder isn't utilized

** how to deal with adults with titles ("Mrs. Margulieux")

Allow for tags (such as hockey or racing) added per day that are aggregated and can be looked up with separate command
    Idea is to allow for tracking of how many hockey games played, for example

Highlight the current word in context

Bugs:
fix axes on graphing
firstDate isn't accurate - isn't picking up 8-08-10, possible bug because it's the first date in there (but test case works)
days are off by one - doesn't pick up the first entry, instead starts with the second
enter new path doesn't work if initial one isn't valid
lookup - length from first to last is wrong


-------------------------------------------------------------------------------------------------------------------------------------------

12-22-17: 
Got Markup class so it actually gets into the proper functions
Fixed tests
Prints to the markup.txt file successfully, with the correct markup, except for punctuation

Next up:
Get punctuation, spacing, and newlines to print successfully into the output file

12-23-17:
Spacing and punctuation is preserved when writing to markup file
    Still is a bit off with spacing (adds an additional space to the start of a new line, for example)
Consolidated two guessNames methods into one
Fixed bugs in guessName (couldn't pick up two names next to each other) and added test
Allow for entering different first name than display name
displayName in WordClass is only for display, and first and last name are the only things looked at for equality

1-01-18:
Added days with at least one usage to lookup output and updated test
Added words with apostrophes to test

1-04-17:
Markup generator now ignores 's endings for names, allowing them to be processed as normal

1-05-18: 
Can now auto assign people referred to by their last names
Use a rolling list of most recent 20 words in the paragraph for context for the markup user
Fixed bug where 's in markup didn't pick up properly
Fixed bug where 's in regular words was removed from markup text

1-06-17:
Fixed bug where "Chuck-A-Rama" would result in "Chuck" in the markup after saying it wasn't a name

'''
