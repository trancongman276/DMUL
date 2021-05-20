import sys
from tokentype import TokenType
from mytoken import Token


class Lexer:

    def __init__(self, src):
        self.src = src + '\n'
        self.curPos = -1
        self.curChar = ''
        self.logger = ''
        self.line = 0
        self.next()

    def next(self):
        self.curPos += 1
        if self.curPos < len(self.src):
            self.curChar = self.src[self.curPos]
        else:
            self.curChar = '\0'

    def curious(self):
        if (self.curPos + 1) < len(self.src):
            return self.src[self.curPos+1]
        return '\0'

    def skipnonsense(self):
        # Skip blank
        while (self.curChar == ' ') or (self.curChar == '\t') or (self.curChar == '\r'):
            self.next()

        # Skip cmt
        if self.curChar == '#':
            while self.curChar != '\n':
                self.next()

    def gettoken(self):
        token = None
        self.skipnonsense()
        # Operator
        if self.curChar == '+':
            if self.curious() == '=':
                self.next()
                token = Token('+=', TokenType.PEQ)
            else:
                token = Token(self.curChar, TokenType.PLUS)

        elif self.curChar == '-':
            if self.curious() == '=':
                self.next()
                token = Token('-=', TokenType.MEQ)
            else:
                token = Token(self.curChar, TokenType.MINUS)

        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.STAR)

        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH)

        elif self.curChar == '=':
            if self.curious() == '=':
                self.next()
                token = Token('==', TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)

        elif self.curChar == '>':
            if self.curious() == '=':
                self.next()
                token = Token('>=', TokenType.GEQ)
            else:
                token = Token(self.curChar, TokenType.GT)

        elif self.curChar == '<':
            if self.curious() == '=':
                self.next()
                token = Token('<=', TokenType.LEQ)
            else:
                token = Token(self.curChar, TokenType.LT)

        elif self.curChar == '!':
            if self.curious() == '=':
                self.next()
                token = Token('!=', TokenType.NOTEQ)
            else:
                self._panik(f"Weird token: '{self.curChar}'")
        
        elif self.curChar == '(':
            token = Token('(', TokenType.OBRACKET)
        
        elif self.curChar == ')':
            token = Token(')', TokenType.CBRACKET)
        
        elif self.curChar == '?':
            token = Token('?', TokenType.QSM)

        # Types and Keyword
        elif self.curChar == '\"':
            self.next()
            startPos = self.curPos
            while self.curChar != '\"':
                self.next()
            token = Token(self.src[startPos:self.curPos], TokenType.STRING)

        elif self.curChar.isdigit():
            startPos = self.curPos
            while self.curious().isdigit():
                self.next()
            if self.curious() == '.':
                self.next()
                if not self.curious().isdigit():
                    self._panik("Wrong digit number format!")
                while self.curious().isdigit():
                    self.next()
            token = Token(self.src[startPos:self.curPos+1], TokenType.NUMBER)

        elif self.curChar.isalpha():
            startPos = self.curPos
            while self.curious().isalnum():
                self.next()
            tkValue = self.src[startPos:self.curPos + 1]
            kind = Token.checktoken(tkValue)
            if kind is not None:
                token = Token(tkValue, kind)
            else:
                token = Token(tkValue, TokenType.ID)

        elif self.curChar == '\n':
            token = Token(self.curChar, TokenType.NEWLINE)
            self.line += 1

        elif self.curChar == '\0':
            token = Token('', TokenType.EOF)

        else:
            self._panik(f"Weird token: '{self.curChar}'")

        self.next()
        self.logger += token.kind.name + '\t' + token.value + '\n'
        return token

    def get_line(self):
        return self.line + 1

    def _panik(self, msg):
        sys.exit(f"ABORT! ABORT!\nLexer paniked: {msg}")

    def makeLog(self):
        with open('temp/.lexer','w+') as f:
            f.write(self.logger)
