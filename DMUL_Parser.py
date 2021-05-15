import sys
from tokentype import TokenType


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.curToken = None
        self.nextToken = None
        self.idList = set()
        self.labelList = set()
        self.visitedLabel = set()

        self.next()
        self.next()

    def next(self):
        self.curToken = self.nextToken
        self.nextToken = self.lexer.gettoken()

    def match(self, kind):
        if not self.checkToken(kind):
            self._panik(f"Expected {kind}, got {self.curToken.kind}")
        self.next()

    def checkToken(self, kind):
        return self.curToken.kind == kind

    def checkcurios(self, kind):
        return self.nextToken.kind == kind

    # Program ::= {Statement}
    def program(self):
        print("PROGRAM")
        while not self.checkToken(TokenType.EOF):
            self.statement()
        for label in self.visitedLabel:
            if label not in self.labelList:
                self._panik(f"Confused label {label}")

    def statement(self):
        # Statement ::= "PRINT" (expression | String) nl
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.next()
            if self.checkToken(TokenType.STRING):
                self.next()
            else:
                self.expr()

        # "IF" cond "THEN" nl {statement} ("ENDIF" nl | "ELSE" nl {statement} "ENDIF" nl)
        elif self.checkToken(TokenType.IF):
            print("STATEMENT-IF")
            self.next()
            self.cond()
            self.match(TokenType.THEN)
            self.nl()

            while not (self.checkToken(TokenType.ENDIF) or self.checkToken(TokenType.ELSE)):
                self.statement()

            if self.checkToken(TokenType.ELSE):
                self.next()
                self.nl()
                while not self.checkToken(TokenType.ENDIF):
                    self.statement()

            self.match(TokenType.ENDIF)

        # "WHILE" cond "DO" {statement} "ENDWHILE" nl
        elif self.checkToken(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.next()
            self.cond()
            self.match(TokenType.DO)
            self.nl()
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()
            self.match(TokenType.ENDWHILE)

        # "LABEL" id nl
        elif self.checkToken(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.next()
            # Check if the current label is existing in labelList or not
            if self.curToken.value in self.labelList:
                self._panik(f"Duplicated label: {self.curToken.value}")
            self.labelList.add(self.curToken.value)
            self.match(TokenType.ID)

        # "GOTO" id nl
        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.next()
            # Add visited label for later check
            self.visitedLabel.add(self.curToken.value)
            self.match(TokenType.ID)

        # "LET" id "=" expression nl
        elif self.checkToken(TokenType.LET):
            print("STATEMENT-LET")
            self.next()
            # Add id if it hasn't existed
            if self.curToken.value not in self.idList:
                self.idList.add(self.curToken.value)
            self.match(TokenType.ID)
            self.match(TokenType.EQ)
            self.expr()

        # "INPUT" id nl
        elif self.checkToken(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.next()
            # check if parameter is declared
            if self.curToken.value not in self.idList:
                self._panik(f"Undeclared parameter: {self.curToken.value}")
            self.match(TokenType.ID)

        else:
            self._panik(f"??? Statement at {self.curToken.value} ({self.curToken.kind.name})")

        self.nl()

    # condition ::= expr ("==" | "!=" | ">" | ">=" | "<" | "<=") expr +
    def cond(self):
        print("CONDITIONAL")
        self.expr()
        if self.iscomparition():
            self.next()
            self.expr()
        else:
            self._panik(f"Expected comparison operation at {self.curToken.value}")
        while self.iscomparition():
            self.next()
            self.expr()

    # expr ::= term | ( "-" | "+" ) term
    def expr(self):
        print("EXPRESSION")
        self.term()
        while self.checkToken(TokenType.PLUS) or \
                self.checkToken(TokenType.MINUS):
            self.next()
            self.term()

    # term ::= unary | ( "/" | "*" ) unary
    def term(self):
        print("TERM")
        self.unary()
        while self.checkToken(TokenType.SLASH) or \
                self.checkToken(TokenType.STAR):
            self.next()
            self.unary()

    # UNARY ::= ( "+" | "-" ) primary
    def unary(self):
        print("UNARY")
        if self.checkToken(TokenType.PLUS) or \
                self.checkToken(TokenType.MINUS):
            self.next()
        self.primary()

    # PRIMARY ::= number | id
    def primary(self):
        print(f"PRIMARY ({self.curToken.value})")
        if self.checkToken(TokenType.NUMBER):
            self.next()
        elif self.checkToken(TokenType.ID):
            # check if parameter is declared
            if self.curToken.value not in self.idList:
                self._panik(f"Undeclared parameter: {self.curToken.value}")
            self.next()
        else:
            self._panik(f"Expected a number or an identity at {self.curToken.value}")

    # nl ::= '\n' +
    def nl(self):
        print("NEWLINE")
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

    def _panik(self, msg):
        sys.exit(f"ABORT ABORT!\n PARSER paniked! {msg}")
