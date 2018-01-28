import re

#Used to represent a single word. This is a full class so markup words can be handled the same way as
#regular words without disrupting the logic. Overriding the toString and comparison methods allow this 
#operation to work

#display name is purely for display and can be different for the same person. First and last name are internal,
#and are utilized for determining if two people are the same
class WordClass:
    rawWord = None
    displayName = None
    firstName = None
    lastName = None

    wasPluralWithApostrophe = False

    MARK_UNDER_START = '[!!'
    MARK_UNDER_END = '!!]'
    MARK_UNDER_DELIMITER = '|'
    MARK_UNDER_FIRSTLAST_DELIMITER = '_'

    @staticmethod
    def addWordOrMarkup(inp_wordOrMarkup, wasPluralWithApostrophe = False):
        return WordClass(inp_wordOrMarkup, wasPluralWithApostrophe)

    def addNameWithMarkupPieces(displayName, firstName, lastName, wasPluralWithApostrophe = False):
        return WordClass(WordClass.buildMarkupString(displayName, firstName, lastName), wasPluralWithApostrophe)

    @staticmethod
    def buildMarkupString(displayName, firstName, lastName):
        markupStr = WordClass.MARK_UNDER_START + displayName + WordClass.MARK_UNDER_DELIMITER + firstName
        markupStr += WordClass.MARK_UNDER_FIRSTLAST_DELIMITER + lastName + WordClass.MARK_UNDER_END
        return markupStr;

    def __init__(self, inp_markup, wasPluralWithApostrophe = False):
        self.rawWord = inp_markup
        markupName = re.compile('^\[!!([^|]+)\|([^_]+)_([^!]+)!!\]$').search(self.rawWord)
        if markupName != None:
            self.displayName = markupName.group(1)
            self.firstName = markupName.group(2)
            self.lastName = markupName.group(3)
        self.wasPluralWithApostrophe = wasPluralWithApostrophe

    def __str__(self):
        return self.toString()

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if type(other) is not WordClass:
            return False
        return self.firstName == other.firstName and self.lastName == other.lastName

    def toString(self):
        if self.displayName != None:
            if self.wasPluralWithApostrophe:
                return self.displayName + "'s"
            return self.displayName
        return self.rawWord

    def strip(self):
        return self.toString().strip()

    def endswith(self, arg):
        return self.toString().endswith(arg) #TODO: will this get confused when plural with apostrophe?

    def printMarkup(self):
        if self.displayName == None:
            return self.toString()
        else:
            markup = WordClass.buildMarkupString(self.displayName, self.firstName, self.lastName)
            if self.wasPluralWithApostrophe:
                return markup + "'s"
            return markup
            


