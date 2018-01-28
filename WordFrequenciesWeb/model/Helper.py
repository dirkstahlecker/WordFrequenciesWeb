import re
from datetime import datetime
import locale

class Helper:
    illegalWordStartCharacters = ['\\','{','}'] #characters that a word can't start with

    @staticmethod
    def daysAsPrettyLength(numDays):
        years = numDays // 365
        months = (numDays - years *  365) // 12
        days = (numDays - years *  365) % 30
        return str(years) + ' years, ' + str(months) + ' months, ' + str(days) + ' days'

    @staticmethod
    def cleanWord(word, preserveCapitalization = False, stripApostropheS = False):
        try:
            word = word.toString()
        except:
            pass
        word = word.strip().lstrip();
        if not preserveCapitalization:
            word = word.lower()
        regex = re.compile('([\w|-|\']*)')
        if stripApostropheS:
            word = word.translate(str.maketrans({'‘':"'",'’':"'"})) #need to change from smart quotes to regular
            if word.endswith("'s"):
                word = word[:-2]
        match = regex.match(word)
        word = match.group(0)
        return word

    @staticmethod
    def makeDateObject(dateStr):
        split1 = dateStr.find('-')
        split2 = dateStr.find('-',split1)
        split2 = split2 + split1 + 1

        month = int(dateStr[:split1])
        day = int(dateStr[split1+1:split2])
        year = int(dateStr[split2+1:])
        #convert year into four digits
        if year < 1000:
            year = year + 2000

        return datetime(year=year, month=month, day=day)

    @staticmethod
    def valid(word):
        if len(word) == 0:
            return False;
        if word[0] in Helper.illegalWordStartCharacters:
            return False
        return True

    #Put date into a format that can be recognized by datetime
    @staticmethod
    def formatDateStringIntoCleanedString(dateStr):
        date = dateStr.strip().lstrip();

        #currently assume they're fairly correctly formatted
        #won't get in here in the first place if they're not
        if re.search('^[0-9]-', date):
            date = '0' + date
        if re.search('-[0-9]-', date):
            date = date[:3] + '0' + date[3:]
        return date

    @staticmethod
    def prettyPrintDate(date):
        return date.strftime('%m-%d-%Y')

    @staticmethod
    def cleanInput(inp):
        return inp.strip().lstrip().lower()

    #return the stripped word, along with the stuff that was stripped off
    #return (beforeStuff, strippedWOrd, afterStuff)
    @staticmethod
    def cleanWordForInitialAdd(word_in):
        if re.match('^\s+$', word_in) != None:
            print('WHAT TO RETURN HERE??') #TODO: error handling
            return ('', word_in, '')
        try:
            #clean word before putting it into the WordClass representation
            firstLetterIndex = re.search('\w|-', word_in).span()[0]
            beforeStuff = word_in[:firstLetterIndex]
            lastLetterIndex = re.search('\w(?!.*\w)', word_in).span()[1]
            afterStuff = word_in[lastLetterIndex:]
            word_str = word_in[firstLetterIndex:lastLetterIndex]
        except:
            #something went wrong, so just go back to defaults
            beforeStuff = ''
            word_str = word_in
            afterStuff = ''



        word = word_in.rstrip('\r\n').strip().lstrip().replace('\\', '')
        word = re.sub('[\s\n\.,;:\}]+$', '', word)
        return (beforeStuff, word_str, afterStuff)




