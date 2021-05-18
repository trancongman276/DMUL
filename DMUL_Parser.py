from mytoken import Token
import sys
from tokentype import TokenType

class Parser:
    def __init__(self, lexer, writter):
        self.writter = writter
        self.lexer = lexer
        self.curToken = None
        self.nextToken = None
        self.idList = set()
        self.labelList = set()
        self.visitedLabel = set()

        self.logger = ""
        self.bCounter = 0
        self.line = 1
        self.tab = 0

        self.next()
        self.next()

    def next(self):
        self.curToken = self.nextToken
        self.nextToken = self.lexer.gettoken()

    def match(self, kind):
        if not self.checkToken(kind):
            self._panik(f"Expected {kind}, got {self.curToken.kind} at line {self.line}")
        self.next()

    def checkToken(self, kind):
        return self.curToken.kind == kind

    def checkcurios(self, kind):
        return self.nextToken.kind == kind

    # Program ::= {Statement}
    def program(self):
        self.logger += "PROGRAM\n"
        while not self.checkToken(TokenType.EOF):
            self.statement()
        for label in self.visitedLabel:
            if label not in self.labelList:
                self._panik(f"Confused label {label}")
        self.writter.write_file()
        self.makeLog()

    def statement(self):
        # Statement ::= "PRINT" (expression | String) nl
        if self.checkToken(TokenType.PRINT):
            self.logger += "STATEMENT-PRINT\n"
            self.next()
            if self.checkToken(TokenType.STRING):
                self.writter.put_line(f"print(\"{self.curToken.value}\")")
                self.next()
            else:
                self.writter.put_code("print(")
                self.expr()
                self.writter.put_code(")\n")

        # "IF" cond "THEN" nl {statement} ("EF" nl | "ELSE" nl {statement} "EF" nl)
        elif self.checkToken(TokenType.IF):
            self.logger += "STATEMENT-IF\n"
            self.writter.put_code("if ")
            self.tab += 1
            self.next()
            self.cond()
            self.match(TokenType.THEN)
            self.writter.put_code(" :")
            self.nl()
            while not (self.checkToken(TokenType.EF) or self.checkToken(TokenType.ELSE)):
                self.writter.put_code("\t"*self.tab)
                self.statement()

            if self.checkToken(TokenType.ELSE):
                self.writter.put_code("else:")
                self.next()
                self.nl()
                while not self.checkToken(TokenType.EF):
                    self.writter.put_code("\t"*self.tab)
                    self.statement()

            self.match(TokenType.EF)
            self.tab -= 1

        # "WHILE" cond "DO" {statement} "ENDWHILE" nl
        elif self.checkToken(TokenType.WHILE):
            self.logger += "STATEMENT-WHILE\n"
            self.next()
            self.cond()
            self.match(TokenType.DO)
            self.nl()
            while not self.checkToken(TokenType.EW):
                self.statement()
            self.match(TokenType.EW)

        # "FOR" id "=" expr "," cond "," expr "ENDFOR"

        # "LABEL" id nl
        elif self.checkToken(TokenType.LABEL):
            self.logger += "STATEMENT-LABEL\n"
            self.next()
            # Check if the current label is existing in labelList or not
            if self.curToken.value in self.labelList:
                self._panik(f"Duplicated label at line {self.line}: {self.curToken.value}")
            self.labelList.add(self.curToken.value)
            self.match(TokenType.ID)

        # "GOTO" id nl
        elif self.checkToken(TokenType.GOTO):
            self.logger += "STATEMENT-GOTO\n"
            self.next()
            # Add visited label for later check
            self.visitedLabel.add(self.curToken.value)
            self.match(TokenType.ID)


        # "LET" id (("=" | "+=" | "-=") expr)  nl
        elif self.checkToken(TokenType.LET):
            self.logger += "STATEMENT-LET\n"
            tempId = None
            self.next()
            # Add id if it hasn't existed
            if self.curToken.value not in self.idList:
                # Check if using the current id 
                if self.checkcurios(TokenType.PEQ) or self.checkcurios(TokenType.MEQ): 
                    self._panik(f"Undeclared parameter at line {self.line}: ({self.curToken.value})")
                # Set for later declaration
                tempId = self.curToken.value
            self.writter.put_code(self.curToken.value)
            self.match(TokenType.ID)
            self.writter.put_code(self.curToken.value)
            if self.checkToken(TokenType.PEQ) or self.checkToken(TokenType.MEQ):
                self.next()
            else:
                self.match(TokenType.EQ)
            self.expr()

            if tempId is not None:
                self.idList.add(tempId)


        # "INPUT" id nl
        elif self.checkToken(TokenType.INPUT):
            self.logger += "STATEMENT-INPUT\n"
            self.next()
            self.writter.put_code(f"{self.nextToken.value} = float(input())")
            self.next()
            # check if parameter is declared
            if self.curToken.value not in self.idList:
                self.idList.add(self.curToken.value)
            self.match(TokenType.ID)

        else:
            self._panik(f"??? Statement at line {self.line}:  {self.curToken.value} ({self.curToken.kind.name})")

        self.nl()

    # condition ::= expr ("==" | "!=" | ">" | ">=" | "<" | "<=") expr 
    def cond(self):
        self.logger += "CONDITIONAL\n"
        self.expr()
        if self.iscomparition():
            self.writter.put_code(self.curToken.value)
            self.next()
            self.expr()
        else:
            self._panik(f"Expected comparison operation at line {self.line}: {self.curToken.value}")
        while self.iscomparition():
            self.writter.put_code(self.curToken.value)
            self.next()
            self.expr()

    # expr ::= term ( "-" | "+" ) term | term
    def expr(self):
        self.logger += "EXPRESSION\n"
        if self.checkToken(TokenType.CBRACKET):
            self._panik("Unexpected ')'")
        self.checkBracket()
        self.term()
        self.checkBracket()
        while self.checkToken(TokenType.PLUS) or \
                self.checkToken(TokenType.MINUS):
            self.writter.put_code(self.curToken.value)
            self.next()
            self.checkBracket()
            self.term()

    # term ::= primary | primary ( "/" | "*" ) primary
    def term(self):
        self.logger += "TERM\n"
        self.primary()
        self.checkBracket()
        while self.checkToken(TokenType.SLASH) or \
                self.checkToken(TokenType.STAR):
            self.writter.put_code(self.curToken.value)
            self.next()
            self.checkBracket()
            self.primary()
            self.checkBracket()

    # PRIMARY ::= number | id
    def primary(self):
        self.logger += f"PRIMARY ({self.curToken.value})\n"
        self.writter.put_code(self.curToken.value)
        if self.checkToken(TokenType.NUMBER):
            self.next()
        elif self.checkToken(TokenType.ID):
            # check if parameter is declared
            if self.curToken.value not in self.idList:
                self._panik(f"Undeclared parameter at line {self.line}: {self.curToken.value}")
            self.next()
        else:
            self._panik(f"Expected a number or an identity at line {self.line}: {self.curToken.value}")

    # nl ::= '\n' +
    def nl(self):
        if not (self.checkcurios(TokenType.EF) or\
                self.checkcurios(TokenType.EOF)):
            self.line += 1
            self.logger += "NEWLINE\n"
            self.writter.put_line("")
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.next()

    def iscomparition(self):
        return self.checkToken(TokenType.GT) or \
               self.checkToken(TokenType.LT) or \
               self.checkToken(TokenType.EQEQ) or \
               self.checkToken(TokenType.GEQ) or \
               self.checkToken(TokenType.LEQ) or \
               self.checkToken(TokenType.NOTEQ)

    def checkBracket(self):
        while self.checkToken(TokenType.OBRACKET):
            self.writter.put_code('(')
            self.bCounter += 1
            self.next()
        while self.checkToken(TokenType.CBRACKET):
            self.writter.put_code(')')
            self.bCounter -= 1
            self.next()

    def _panik(self, msg):
        print(self.logger)
        print(self.idList)
        sys.exit(f"ABORT ABORT!\n PARSER paniked! {msg}")

    def makeLog(self):
        self.lexer.makeLog()
        with open('temp/.parser','w+') as f:
            f.write(self.logger)
        with open('temp/symbol_table','w+') as f:
            for id in self.idList:
                f.write(id)
