import io
import re
import os
import errno
import sys
import colorama
import six
import platform
import codecs
import subprocess
from rfctools_common import log


if six.PY2:
    import subprocess32
    subprocess = subprocess32
else:
    import subprocess


class RfcLintError(Exception):
    """ RFC Lint internal errors """
    def __init__(self, msg, filename=None, line_no=0):
        self.msg = msg
        self.message = msg
        self.position = line_no
        self.filename = filename
        self.line = line_no


def ReplaceWithSpace(exc):
    if isinstance(exc, UnicodeDecodeError):
        return u' '
    elif isinstance(exc, UnicodeEncodeError):
        if six.PY2:
            return ((exc.end-exc.start)*u' ', exc.end)
        else:
            return (bytes((exc.end-exc.start)*[32]), exc.end)
    else:
        raise TypeError("can't handle %s" % type(exc).__name__)


CheckAttributes = {
    "title": ['ascii', 'abbrev'],
    'seriesInfo': ['name', 'asciiName', 'value', 'asciiValue'],
    "author": ['asciiFullname', 'asciiInitials', 'asciiSurname', 'fullname', 'surname', 'initials'],
    'city': ['ascii'],
    'code': ['ascii'],
    'country': ['ascii'],
    'region': ['ascii'],
    'street': ['ascii'],
    'blockquote': ['quotedFrom'],
    'iref': ['item', 'subitem'],
    }

CutNodes = {
    'annotation': 1,
    'area': 1,
    'artwork': 2,
    'blockquote': 2,
    'city': 1,
    'cref': 1,
    'code': 1,
    'country': 1,
    'dd': 2,
    'dt': 1,
    'email': 1,
    'keyword': 1,
    'li': 2,
    'name': 1,
    'organization': 1,
    'phone': 1,
    'postalLine': 1,
    'refcontent': 1,
    'region': 1,
    'sourcecode': 1,
    'street': 1,
    "t": 1,
    'td': 2,
    'th': 2,
    "title": 1,
    'uri': 1,
    'workgroup': 1,
}

# colorama.init()

SpellerColors = {
    'green': colorama.Fore.GREEN,
    'none': '',
    'red': colorama.Fore.RED,
    'bright': colorama.Style.BRIGHT
}
# BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


class Speller(object):
    """ Object to deal with processing spelling and duplicates """
    def __init__(self, config):
        program = config.get('spell', 'program')
        self.suggest = config.getBoolean('spell', 'suggest', True)
        self.window = config.getInt('spell', 'window', 15)
        coloring = config.get('spell', 'color')
        if coloring and coloring in SpellerColors:
            self.color_start = SpellerColors[coloring]
            self.color_end = colorama.Style.RESET_ALL
            if self.color_start == '':
                self.color_end = self.color_start
        elif os.name == 'nt':
            self.color_start = ''
            self.color_end = ''
        else:
            self.color_start = colorama.Style.BRIGHT
            self.color_end = colorama.Style.RESET_ALL

        if program:
            look_for = which(program)
            if not look_for and os.name == 'nt':
                look_for = which(program + '.exe')
            if not look_for:
                raise RfcLintError("The program '{0}' does not exist or is not executable".
                                   format(program))
            program = look_for
        else:
            if os.name == "nt":
                look_for = "aspell.exe"
                program = which(look_for)
                if not program:
                    program = which("c:\\Program Files (x86)\\Aspell\\bin\\aspell.exe")
            else:
                look_for = "aspell"
                program = which(look_for)
            if not program:
                raise RfcLintError("The program '{0}' does not exist or is not executable".
                                   format(look_for))

        spellBaseName = os.path.basename(program)
        spellBaseName = spellBaseName.replace('.exe', '')

        # I want to know what the program and version really are

        p = subprocess.Popen([program, "-v"], stdout=subprocess.PIPE)
        (versionOut, stderr) = p.communicate()
        """
        if p.returncode != 0:
            raise RfcLintError("The program '{0}' executed with an error code {1}".
                               format(program, p.returncode))
        """

        m = re.match(r".*International Ispell Version [\d.]+ \(but really (\w+) ([\d.]+).*",
                     versionOut.decode('utf-8'))
        if m is None:
            raise RfcLintError("Error starting the spelling program\n{0}".format(line))

        if m.group(1).lower() != spellBaseName:
            raise RfcLintError("Error: The wrong spelling program was started.  Expected"
                               "{0} and got {1}".format(spellBaseName, m.group(1)))

        codecs.register_error('replaceWithSpace', ReplaceWithSpace)

        self.iso8859 = False
        if spellBaseName == 'aspell':
            log.note("xx - " + m.group(2))
            if m.group(2)[:3] == '0.5':
                # This version does not support utf-8
                self.iso8859 = True
                log.note("Use iso8859")
        elif spellBaseName == 'hunspell':
            # minumum version of hunspell is 1.1.6, but that is probably not something
            # we would find in the wild anymore.  We are therefore not going to check it.
            # However, right now the only version I have for Windows does not support utf-8
            # so until I get a better version, force the use of iso8859 there.
            if os.name == 'nt':
                self.iso8859 = True
                log.note("Use iso8859")

        # now let's build the full command

        cmdLine = [program, '-a']  # always use pipe mode
        dicts = config.getList('spell', 'dictionaries')
        if dicts:
            dictList = ''
            for dict in dicts:
                if spellBaseName == 'hunspell':
                    dict = dict + '.dic'
                if os.path.isabs(dict):
                    dict2 = dict
                else:
                    dict2 = os.path.join(os.getcwd(), dict)
                dict2 = os.path.normpath(dict2)
                if not os.path.exists(dict2):
                    log.error("Additional Dictionary '{0}' ignored because it was not found".
                              format(dict.replace('.dic', '')))
                    continue
                if spellBaseName == 'aspell':
                    cmdLine.append("--add-extra-dicts")
                    cmdLine.append(dict2)
                else:
                    dictList = dictList + "," + dict2.replace('.dic', '')
            if spellBaseName == 'hunspell':
                cmdLine.append('-d')
                cmdLine.append("en_US" + dictList)

        dict = config.get('spell', 'personal')
        if dict:
            if os.path.isabs(dict):
                dict2 = dict
            else:
                dict2 = os.path.join(os.getcwd(), dict)
            dict2 = os.path.normpath(dict2)
            if not os.path.exists(dict2):
                log.error("Personal Dictionary '{0}' ignored because it was not found".
                          format(dict))
            else:
                cmdLine.append('-p')
                cmdLine.append(dict2)

        if self.iso8859:
            if spellBaseName == 'aspell':
                cmdLine.append('--encoding=iso8859-1')
            else:
                # Make sure if we have a better version of hunspell that it will do the right thing
                cmdLine.append('-i iso-8859-1')
        elif spellBaseName == 'hunspell':
            cmdLine.append('-i utf-8')

        log.note("spell command = '{0}'".format(" ".join(cmdLine)))
        self.p = subprocess.Popen(cmdLine,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        if six.PY2:
            if os.name == 'nt':
                self.stdin = codecs.getwriter('iso-8859-1')(self.p.stdin)
                self.stdout = self.p.stdout
            else:
                self.stdin = codecs.getwriter('utf8')(self.p.stdin)
                self.stdout = self.p.stdout
                # self.stdout = codecs.getreader('utf8')(self.p.stdout)
        else:
            if self.iso8859:
                self.stdin = io.TextIOWrapper(self.p.stdin, encoding='iso-8859-1',
                                              errors='replaceWithSpace', line_buffering=True)
                self.stdout = io.TextIOWrapper(self.p.stdout, encoding='iso-8859-1',
                                               errors='replaceWithSpace')
            else:
                self.stdin = io.TextIOWrapper(self.p.stdin, encoding='utf-8', line_buffering=True)
                self.stdout = io.TextIOWrapper(self.p.stdout, encoding='utf-8')

        #  Check that we got a good return
        line = self.stdout.readline()
        log.note(line)

        self.word_re = re.compile(r'(\W*\w+\W*)', re.UNICODE | re.MULTILINE)
        # self.word_re = re.compile(r'\w+', re.UNICODE | re.MULTILINE)
        self.aspell_re = re.compile(r".\s(\S+)\s(\d+)\s*((\d+): (.+))?", re.UNICODE)

    def processLine(self, allWords):
        """
        Process each individual set of words and return the errors found
        allWords is a tuple of (text string, tree element)
        returned is an array of tuples each tuple consisting of
        ( What the error is ('&' or '#'),
          What the word in error is,
          The set of alternative words (None for '#'),
          The offset in the string of the word,
          The word string,
          The tree node
        )
        """
        result = []
        setNo = 0
        for wordSet in allWords:
            newLine = u'^ ' + wordSet[0] + u'\n'
            if self.iso8859:
                log.note(u"Pre Encode = " + newLine)
                newLine = newLine.encode('iso-8859-1', 'replaceWithSpace')
                newLine = newLine.decode('iso-8859-1')
            else:
                newLine = newLine  # .encode('utf-8')
            log.note(newLine)
            self.stdin.write(newLine)

            index = 0
            running = 0
            while True:
                line = self.stdout.readline()
                if six.PY2:
                    if self.iso8859:
                        #  log.note(" ".join("{:02x}".format(c) for c in line))
                        line = line.decode('iso-8859-1')
                    else:
                        line = line.decode('utf-8')
                line = line.strip()
                log.note('spell out line = ' + line)

                if len(line) == 0:
                    break

                if line[0] == '*':
                    continue

                m = self.aspell_re.match(line)
                if not m:
                    log.error("Internal error trying to match the line '{0}'".format(line))
                    continue

                if line[0] == '#':
                    offset = int(m.group(2))
                    options = None
                elif line[0] == '&':
                    offset = int(m.group(4))
                    options = m.group(5)
                else:
                    log.error("internal error - aspell says line is '{0}'".format(line))
                    continue

                tuple = (line[0], offset, wordSet[1], m.group(1), options, setNo)
                result.append(tuple)
            setNo += 1

        return result

    def processTree(self, tree):
        # log.warn("processTree - look at node {0}".format(tree.tag))
        if tree.tag in CheckAttributes:
            self.checkAttributes(tree)
        if tree.tag in CutNodes:
            self.checkTree(tree)
        for node in tree.iterchildren():
            self.processTree(node)

    def checkTree(self, tree):
        wordSet = self.getWords(tree)
        results = self.processLine(wordSet)

        self.processResults(wordSet, results, None)

        # s = " ".join(words[max(0, i-10):min(len(words), i+10)])
        # s = s.replace(words[i], colorama.Fore.GREEN + ">>>" + words[i] + "<<<" +
        #       colorama.Style.RESET_ALL)
        # log.warn(s)
        # log.warn(results[i][results[i].rfind(':')+2:])

    def getWords(self, tree):
        if tree.text:
            for x in tree.text.splitlines():
                ll = x.strip()
                if ll:
                    words = [(ll, tree)]
        else:
            words = []

        for node in tree.iterchildren():
            if node.tag in CutNodes:
                continue
            words += self.getWords(node)

            if node.tail:
                words += [(node.tail, tree)]

        return words

    def checkAttributes(self, tree):
        for attr in CheckAttributes[tree.tag]:
            if attr not in tree.attrib:
                continue
            words = [(tree.attrib[attr], tree)]
            results = self.processLine(words)
            self.processResults(words, results, attr)

    def processResults(self, wordSet, results, attributeName):
        """  Process the results coming from a spell check operation """

        matchGroups = []
        allWords = []
        for words in wordSet:
            xx = self.word_re.finditer(words[0])
            for w in xx:
                if w:
                    matchGroups.append((w, words[1]))
                    allWords.append(w.group(1))
                    if allWords[-1][-1] not in [' ', '-', "'"]:
                        allWords[-1] += ' '

        for r in results:
            if attributeName:
                log.error("Misspelled word '{0}' in attribute '{1}'".format(r[3], attributeName),
                          where=r[2])
            else:
                log.error(u"Misspelled word was found '{0}'".format(r[3]), where=r[2])
            if self.window > 0:
                q = self.wordIndex(r[1], r[2], matchGroups)
                if q >= 0:
                    ctx = ""
                    if q > 0:
                        ctx = "".join(allWords[max(0, q-self.window):q])
                    ctx += self.color_start + allWords[q] + self.color_end
                    if q < len(allWords):
                        ctx += "".join(allWords[q+1:min(q+self.window+1, len(allWords))])
                    log.error(ctx, additional=2)
            if self.suggest and r[4]:
                log.error(r[4], additional=2)

        # check for dups
        last = None
        for (m, el) in matchGroups:
            for g in m.groups():
                if last:
                    # print("compare '{0}' and '{1}'".format(last, g))
                    if last == g:
                        log.error("Duplicate word found '{0}'".format(last), where=el)
                last = g

    def wordIndex(self, offset, el, matchArray):
        """
        Given an offset and element, find the index in the matchArray that matches
        """

        for i in range(len(matchArray)):
            m = matchArray[i]
            if m[1] == el and \
               (m[0].start(1) <= offset and offset <= m[0].end(1)):
                return i
        return -1
