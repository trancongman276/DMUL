from mytoken import Token
import sys
from tokentype import TokenType

class Parser:
    def __init__(self, lexer, writter):
        self.writter = writter
        self.lexer = lexer
        self.curToken = None
        self.nextToken = None
        self.idList = {}
        self.labelList = set()
        self.visitedLabel = set()

        self.logger = ""
        self.bCounter = 0
        self.line = 1
        self.tab = 0
        self.scope = 0

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
                self.writter.put_code(f"print(\"{self.curToken.value}\")")
                self.next()
            else:
                self.writter.put_code("print(")
                self.expr()
                self.writter.put_code(")")

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
            self.scope += 1
            while not (self.checkToken(TokenType.EF) or self.checkToken(TokenType.ELSE)):
                self.writter.put_code("\t"*self.tab)
                self.statement()
            self.removeId()
            if self.checkToken(TokenType.ELSE):
                self.writter.put_code("else:")
                self.next()
                self.nl()
                self.scope += 1
                while not self.checkToken(TokenType.EF):
                    self.writter.put_code("\t"*self.tab)
                    self.statement()
                self.removeId()
            self.match(TokenType.EF)
            self.tab -= 1

        # "WHILE" cond "DO" {statement} "EW" nl
        elif self.checkToken(TokenType.WHILE):
            self.logger += "STATEMENT-WHILE\n"
            self.writter.put_code("while ")
            self.next()
            self.cond()
            self.match(TokenType.DO)
            self.writter.put_code(":")
            self.nl()
            self.scope += 1
            self.tab += 1
            while not self.checkToken(TokenType.EW):
                self.writter.put_code("\t"*self.tab)
                self.statement()
            self.removeId()
            self.match(TokenType.EW)
            self.tab -= 1

        # "FOR" "START" id "=" number "WITHIN" cond "EXEC" id + expr nl {statement} "EFO"
        elif self.checkToken(TokenType.FOR):
            self.logger += "STATEMENT-FOR\n"
            temp_id = None
            init = False
            self.next()
            self.match(TokenType.START)
            if self.curToken.value not in self.idList:
                self.idList[self.curToken.value] = self.scope
                temp_id = self.curToken.value
                self.writter.put_code(f"{temp_id}")
                init = True
            else: self.writter.put_code(self.curToken.value)
            self.next()
            self.match(TokenType.EQ)
            self.writter.put_code("=")
            self.expr()
            self.writter.put_code("\nwhile ")
            self.match(TokenType.WITHIN)
            self.cond()
            self.writter.put_code(":")
            self.match(TokenType.EXEC)
            self.expr(put_code=False)
            self.nl()
            self.tab += 1
            self.scope += 1
            while not self.checkToken(TokenType.EFO):
                self.writter.put_code("\t"*self.tab)
                self.statement()
            self.writter.put_code("\t"*self.tab + f"{temp_id}=")
            self.writter.pop_temp()
            self.removeId()
            self.match(TokenType.EFO)
            self.tab -= 1
            if init: del self.idList[temp_id]
            
        # "LOOP" nl {statement} "UNTIL" cond 
        elif self.checkToken(TokenType.LOOP):
            self.logger += "STATEMENT-LOOP\n"
            self.next()
            self.writter.put_code("while True:")
            self.tab += 1
            self.nl()
            self.scope += 1
            while not self.checkToken(TokenType.UNTIL):
                self.writter.put_code("\t"*self.tab)
                self.statement()
            self.removeId()
            self.match(TokenType.UNTIL)
            self.writter.put_code("\t"*self.tab)
            self.writter.put_code("if ")
            self.cond()
            self.writter.put_code(": break")
            self.tab -= 1

        # "SWITCH" id nl ("INCASE" cond(?) "SO" nl {statement} "ESO" nl | 
        #                   "OTHERCASE" "SO" nl {statement} "ESO" nl "ESW")
        elif self.checkToken(TokenType.SWITCH):
            self.logger += "STATEMENT-SWITCH\n"
            self.next()
            id = self.curToken.value
            if self.curToken.value not in self.idList:
                self._panik(f"Undeclared parameter at line {self.line}: {self.curToken.value}")
            self.match(TokenType.ID)
            self.nl(put_line=False)
            first_if = True
            while self.checkToken(TokenType.INCASE) or \
                    self.checkToken(TokenType.OTHERCASE):
                if not self.checkToken(TokenType.OTHERCASE):
                    if first_if: 
                        self.writter.put_code("if ")
                        self.tab += 1
                        first_if = False
                    else:
                        self.writter.put_code("\n"+"\t"*(self.tab-1)+"elif ")
                    self.next()
                    self.cond(id) # the question mark parameter ?
                else:
                    self.writter.put_code("\n"+"\t"*(self.tab-1)+"else")
                    self.next()
                self.match(TokenType.SO)
                self.writter.put_code(":")
                self.nl()
                self.scope += 1
                while not self.checkToken(TokenType.ESO):
                    self.writter.put_code("\t"*self.tab)
                    self.statement()
                self.removeId()
                self.match(TokenType.ESO)
                self.nl(put_line=False)
            self.match(TokenType.ESW)
            self.tab -= 1

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
                self.idList[tempId] = self.scope


        # "INPUT" id nl
        elif self.checkToken(TokenType.INPUT):
            self.logger += "STATEMENT-INPUT\n"
            self.next()
            self.writter.put_code(f"{self.nextToken.value} = float(input())")
            self.next()
            # check if parameter is declared
            if self.curToken.value not in self.idList[self.scope]:
                self.idList[self.curToken.value] = self.scope
            self.match(TokenType.ID)

        else:
            self._panik(f"??? Statement at line {self.line}:  {self.curToken.value} ({self.curToken.kind.name})")

        self.nl()

    # condition ::= expr ("==" | "!=" | ">" | ">=" | "<" | "<=") expr 
    def cond(self, id = None):
        self.logger += "CONDITIONAL\n"
        self.checkBracket()
        if id is not None:
            check = False # check if the lhs is the "?" or not
            if self.checkToken(TokenType.QSM):
                check = True
                self.writter.put_code(id)
                self.next()
            else:
                self.expr()
        else:
            self.expr()
        if self.iscomparition():
            self.writter.put_code(self.curToken.value)
            self.next()
            if id is not None:
                if check and self.checkToken(TokenType.QSM):
                    self._panik(f"Unexpected '?' at line: {self.line}")
                if self.checkToken(TokenType.QSM):
                    check = True
                    self.writter.put_code(id)
                    self.next()
                else:
                    self.expr()
            else:
                self.expr()
        else:
            self._panik(f"Expected comparison operation at line {self.line}: {self.curToken.value}")
        self.checkBracket()
        while self.iscomparition():
            self.writter.put_code(self.curToken.value)
            self.next()
            if id is not None:
                if check and self.checkToken(TokenType.QSM):
                    self._panik(f"Unexpected '?' at line: {self.line}")
                if self.checkToken(TokenType.QSM):
                    check = True
                    self.writter.put_code(id)
                    self.next()
                else:
                    self.expr()
            else:
                self.expr()
            self.checkBracket()


    # expr ::= term ( "-" | "+" ) term | term
    def expr(self, put_code=True):
        self.logger += "EXPRESSION\n"
        if self.checkToken(TokenType.CBRACKET):
            self._panik("Unexpected ')'")
        self.checkBracket()
        self.term(put_code)
        self.checkBracket()
        while self.checkToken(TokenType.PLUS) or \
                self.checkToken(TokenType.MINUS):
            if put_code: 
                self.writter.put_code(self.curToken.value)
            else: self.writter.put_temp(self.curToken.value)
            self.next()
            self.checkBracket()
            self.term(put_code)

    # term ::= primary | primary ( "/" | "*" ) primary
    def term(self, put_code=True):
        self.logger += "TERM\n"
        self.primary(put_code)
        self.checkBracket()
        while self.checkToken(TokenType.SLASH) or \
                self.checkToken(TokenType.STAR):
            if put_code: 
                self.writter.put_code(self.curToken.value)
            else: self.writter.put_temp(self.curToken.value)
            self.next()
            self.checkBracket()
            self.primary(put_code)
            self.checkBracket()

    # PRIMARY ::= number | id
    def primary(self, put_code=True):
        self.logger += f"PRIMARY ({self.curToken.value})\n"
        if put_code: 
            self.writter.put_code(self.curToken.value)
        else: self.writter.put_temp(self.curToken.value)
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
    def nl(self, put_line=True):
        if not (self.checkcurios(TokenType.EF) or\
                self.checkcurios(TokenType.EOF) or\
                self.checkcurios(TokenType.ESW) or\
                self.checkcurios(TokenType.ESO) or\
                self.checkcurios(TokenType.EW)):
            self.line += 1
            self.logger += "NEWLINE\n"
            if put_line: self.writter.put_code("\n")
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.line += 1
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

    def removeId(self):
        idL = list(self.idList.keys())
        for i in range(len(idL)-1,0,-1):
            if self.idList[idL[i]] == self.scope:
                del self.idList[idL[i]]
            else: break
        self.scope -= 1

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
