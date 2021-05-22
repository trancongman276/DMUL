import sys
from Token.tokentype import TokenType
from Utils.scope import Inner
from Utils.tree import Tree

class Parser:
    def __init__(self, lexer, writter):
        self.writter = writter
        self.lexer = lexer
        self.tree = Tree()
        self.curToken = None
        self.nextToken = None
        self.idList = {}
        self.defaultConst = ['PI','E']
        self.defaultFunc = {'SIN':1,'COS':1,'TAN':1,'POWER':2,'SQRT':1,\
                                'FACTORIAL':1,'DEGREE2RAD':1,'ABS':1}
        self.funcList = {} 
        self.visitedFunc = set()
        self.visitedStatement = set()
        self.usedConst = set()

        self.logger = ""
        self.bCounter = 0
        self.tab = 0
        self.treeId = 0
        self.parentId = 0

        self.curScope = Inner(parentId=[], parentConst=self.defaultConst, name="glob")
        
        self.inFunc = False

        self.next()
        self.next()

    def next(self):
        self.curToken = self.nextToken
        self.nextToken = self.lexer.gettoken()

    def match(self, kind):
        if not self.checkToken(kind):
            self._panik(f"Expected {kind}, got {self.curToken.kind} at line {self.lexer.get_line()}")
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
        self.tree.putNode(0, self.treeId+1,'EOF')
        for func in self.visitedFunc:
            if func not in self.funcList and\
                    func not in self.defaultFunc:
                print(f"[WARN] Un-touched function {func}")
        self.writter.write_file()
        self.makeLog()

    def statement(self):
        self.put_node('STATEMENT')
        self.parentId = self.treeId
        # Skip head newlines
        while self.checkToken(TokenType.NEWLINE):
            self.next()
        self.put_node(self.curToken.value)

        self.visitedStatement.add(self.curToken.value)

        # Statement ::= "PRINT" (expression | String) nl
        if self.checkToken(TokenType.PRINT):
            self.logger += "STATEMENT-PRINT\n"
            self.next()
            if self.checkToken(TokenType.STRING):
                self.put_node("STRING")
                self.put_code(f"print(\"{self.curToken.value}\")")
                self.next()
            else:
                self.put_code("print(")
                self.expr()
                self.put_code(")")

        # "IF" cond "THEN" nl {statement} ("EIF" nl | "ELSE" nl {statement} "EIF" nl)
        elif self.checkToken(TokenType.IF):
            self.logger += "STATEMENT-IF\n"
            self.put_code("if ")
            self.tab += 1
            self.next()
            self.cond()
            self.match(TokenType.THEN)
            self.put_node("THEN")
            self.put_code(" :")
            self.nl()
            lastParent = self.parentId
            parentScope = self.create_scope()
            while not (self.checkToken(TokenType.EIF) or self.checkToken(TokenType.ELSE)):
                self.put_code("\t"*self.tab)
                self.statement()
            if self.checkToken(TokenType.ELSE):
                self.parentId = lastParent
                self.put_node("ELSE")
                self.put_code("\t"*(self.tab-1)+"else:")
                self.next()
                self.nl()
                parentScope_else = self.create_scope()
                while not self.checkToken(TokenType.EIF):
                    self.put_code("\t"*self.tab)
                    self.statement()
                parentScope_else.inner.append(self.curScope)
                self.curScope = parentScope_else
            self.match(TokenType.EIF)
            self.parentId = lastParent
            self.put_node('EIF')
            parentScope.inner.append(self.curScope)
            self.curScope = parentScope
            self.tab -= 1

        # "WHILE" cond "DO" {statement} "EWH" nl
        elif self.checkToken(TokenType.WHILE):
            self.logger += "STATEMENT-WHILE\n"
            self.put_code("while ")
            self.next()
            self.cond()
            self.match(TokenType.DO)
            self.put_node('DO')
            self.put_code(":")
            self.nl()
            parentScope = self.create_scope()
            self.tab += 1
            lastParent = self.parentId
            while not self.checkToken(TokenType.EWH):
                self.put_code("\t"*self.tab)
                self.statement()
            self.match(TokenType.EWH)
            self.parentId = lastParent
            self.put_node('EWH')
            parentScope.inner.append(self.curScope)
            self.curScope = parentScope
            self.tab -= 1

        # "FOR" "START" id "=" number "WITHIN" cond "EXEC" id + expr nl {statement} "EFO"
        elif self.checkToken(TokenType.FOR):
            self.logger += "STATEMENT-FOR\n"
            temp_id = None
            init = False
            parentScope = self.create_scope()
            self.next()
            self.match(TokenType.START)
            self.put_node("START")
            if not self.curScope.checkId(self.curToken.value):
                self.curScope.idList.append(self.curToken.value)
                temp_id = self.curToken.value
                self.put_code(f"{temp_id}")
                init = True
            else: self.put_code(self.curToken.value)
            self.put_node(self.curToken.value)
            self.next()
            self.match(TokenType.EQ)
            self.put_node("=")
            self.put_code("=")
            self.expr()
            self.put_node("WITHIN")
            self.put_code("\n"+"\t"*self.tab + "while ")
            self.match(TokenType.WITHIN)
            self.cond()
            self.put_node("EXEC")
            self.put_code(":")
            self.match(TokenType.EXEC)
            self.expr(put_code=False)
            self.nl()
            self.tab += 1            
            lastParent = self.parentId
            while not self.checkToken(TokenType.EFO):
                self.put_code("\t"*self.tab)
                self.statement()
            self.put_code("\t"*self.tab + f"{temp_id}=")
            self.writter.pop_temp()
            self.match(TokenType.EFO)
            self.parentId = lastParent
            self.put_node("EFO")
            parentScope.inner.append(self.curScope)
            self.curScope = parentScope
            self.tab -= 1
            # if init: del self.idList[temp_id]
            
        # "LOOP" nl {statement} "UNTIL" cond 
        elif self.checkToken(TokenType.LOOP):
            self.logger += "STATEMENT-LOOP\n"
            self.next()
            self.put_code("while True:")
            self.tab += 1
            self.nl()
            lastParent = self.parentId
            parentScope = self.create_scope()
            while not self.checkToken(TokenType.UNTIL):
                self.put_code("\t"*self.tab)
                self.statement()
            self.parentId = lastParent
            self.match(TokenType.UNTIL)
            self.put_node("UNTIL")
            self.put_code("\t"*self.tab)
            self.put_code("if ")
            self.cond()
            self.put_code(": break")
            parentScope.inner.append(self.curScope)
            self.curScope = parentScope
            self.tab -= 1

        # "SWITCH" id nl ("INCASE" cond(?) "SO" nl {statement} "ESO" nl | 
        #                   "OTHERCASE" "SO" nl {statement} "ESO" nl "ESW")
        elif self.checkToken(TokenType.SWITCH):
            self.logger += "STATEMENT-SWITCH\n"
            self.next()
            id = self.curToken.value
            if not self.curScope.checkId(self.curToken.value):
                self._panik(f"Undeclared parameter at line {self.lexer.get_line()}: {self.curToken.value}")
            self.match(TokenType.ID)
            self.put_node(id)
            self.nl(put_line=False)
            first_if = True
            while self.checkToken(TokenType.INCASE) or \
                    self.checkToken(TokenType.OTHERCASE):
                self.put_node(self.curToken.value)
                if not self.checkToken(TokenType.OTHERCASE):
                    if first_if: 
                        self.put_code("if ")
                        self.tab += 1
                        first_if = False
                    else:
                        self.put_code("\n"+"\t"*(self.tab-1)+"elif ")
                    self.next()
                    self.cond(id) # the question mark parameter ?
                else:
                    self.put_code("\n"+"\t"*(self.tab-1)+"else")
                    self.next()
                self.put_node(self.curToken.value)
                self.match(TokenType.SO)
                self.put_code(":")
                self.nl()
                parentScope = self.create_scope()
                lastParent = self.parentId
                while not self.checkToken(TokenType.ESO):
                    self.put_code("\t"*self.tab)
                    self.statement()
                self.parentId = lastParent
                self.put_node(self.curToken.value)
                self.match(TokenType.ESO)
                self.nl(put_line=False)
                parentScope.inner.append(self.curScope)
                self.curScope = parentScope
            self.put_node(self.curToken.value)
            self.match(TokenType.ESW)
            self.tab -= 1

        # "FUNC" id "(" id ")" nl expr "EFU" expr
        elif self.checkToken(TokenType.FUNC):
            self.logger += "STATEMENT-FUNC\n"
            self.next()
            parentScope = self.create_scope(name='func')
            self.inFunc = True
            funcName = self.curToken.value
            initList = set()
            # Check if the current func is existing in funcList or not
            if funcName in self.funcList:
                self._panik(f"Duplicated function at line {self.lexer.get_line()}: {funcName}")
            self.funcList[funcName] = 0
            self.put_node(funcName)
            self.put_code(f"def {funcName}(")
            self.match(TokenType.ID)
            self.put_node(self.curToken.value)
            self.match(TokenType.OBRACKET)

            while not self.checkToken(TokenType.CBRACKET):
                if self.curToken.value in initList:
                    self._panik(f"Duplicated variable at line {self.lexer.get_line()}")
                initList.add(self.curToken.value)
                # if not self.curScope.checkId(self.curToken.value):
                self.curScope.idList.append(self.curToken.value)
                if self.checkcurios(TokenType.CBRACKET):
                    self.put_code(f"{self.curToken.value}")
                    self.put_node(self.curToken.value)
                    self.next()
                else:
                    self.put_code(f"{self.curToken.value},")
                    self.put_node(self.curToken.value)
                    self.next()
                    self.put_node(self.curToken.value)
                    self.match(TokenType.SEPARATOR)

            self.put_node(self.curToken.value)
            self.match(TokenType.CBRACKET)
            self.funcList[funcName] = len(initList)
            self.put_code(f"):")
            self.nl()
            self.tab += 1
            lastParent = self.parentId
            while not self.checkToken(TokenType.EFU):
                self.put_code("\t"*self.tab)
                self.statement()
            self.parentId = lastParent
            self.put_node(self.curToken.value)
            self.match(TokenType.EFU)
            self.put_code("\t"*self.tab + "return ")
            self.expr()
            self.put_code("\n")
            self.inFunc = False
            parentScope.inner.append(self.curScope)
            self.curScope = parentScope
            self.tab -= 1

        # "LET" id (("=" | "+=" | "-=") expr)  nl
        elif self.checkToken(TokenType.LET):
            self.logger += "STATEMENT-LET\n"
            tempId = None
            self.next()
            
            # Check changing const
            if self.curScope.checkConst(self.curToken.value):
                self._panik(f"Error at line {self.lexer.get_line()} Cannot change the constant!")

            # Add id if it hasn't existed
            if not self.curScope.checkId(self.curToken.value):
                # Check if using the current id 
                if self.checkcurios(TokenType.PEQ) or self.checkcurios(TokenType.MEQ): 
                    self._panik(f"Undeclared parameter at line {self.lexer.get_line()}: ({self.curToken.value})")

                # Set for later declaration
                tempId = self.curToken.value
                
            self.put_code(self.curToken.value)
            self.put_node(self.curToken.value)
            self.match(TokenType.ID)
            self.put_node(self.curToken.value)
            self.put_code(self.curToken.value)
            if self.checkToken(TokenType.PEQ) or self.checkToken(TokenType.MEQ):
                self.next()
            else:
                self.match(TokenType.EQ)
            self.expr()

            if tempId is not None:
                self.curScope.idList.append(tempId)

        # "CONST" id "=" expr
        elif self.checkToken(TokenType.CONST):
            self.logger += "STATEMENT-CONST\n"
            self.next()
            if self.curScope.checkId(self.curToken.value) or\
                self.curScope.checkConst(self.curToken.value):
                self._panik(f"Unexpected parameter at line {self.lexer.get_line()}: {self.curToken.value}")
            self.curScope.constId.append(self.curToken.value)
            self.put_node(self.curToken.value)
            self.put_code(f'{self.curToken.value}=')
            self.match(TokenType.ID)
            self.put_node(self.curToken.value)
            self.match(TokenType.EQ)
            self.expr()

        # "INPUT" id nl
        elif self.checkToken(TokenType.INPUT):
            self.logger += "STATEMENT-INPUT\n"
            self.next()
            self.put_code(f"{self.curToken.value} = float(input())")
            # check if parameter is declared
            if not self.curScope.checkId(self.curToken.value):
                self.curScope.idList.append(self.curToken.value)
            self.put_node(self.curToken.value)
            self.match(TokenType.ID)
        
        else:
            self._panik(f"??? Statement at line {self.lexer.get_line()}:  {self.curToken.value} ({self.curToken.kind.name})")

        self.nl()

    # condition ::= expr ("==" | "!=" | ">" | ">=" | "<" | "<=") expr 
    def cond(self, id = None):
        self.logger += "CONDITIONAL\n"
        self.put_node("cond")
        lastParent = self.parentId
        self.parentId = self.treeId

        self.checkBracket()
        # Check special cond in switch-incase
        if id is not None:
            check = False # check if the lhs is the "?" or not
            if self.checkToken(TokenType.QSM):
                check = True
                self.put_code(id)
                self.next()
            else:
                self.expr()
        else:
            self.expr()
        if self.iscomparition():
            self.put_code(self.curToken.value)
            self.put_node(self.curToken.value)
            self.next()
            if id is not None:
                if check and self.checkToken(TokenType.QSM):
                    self._panik(f"Unexpected '?' at line: {self.lexer.get_line()}")
                if self.checkToken(TokenType.QSM):
                    check = True
                    self.put_code(id)
                    self.next()
                else:
                    self.expr()
            else:
                self.expr()
        else:
            self._panik(f"Expected comparison operation at line {self.lexer.get_line()}: {self.curToken.value}")
        self.checkBracket()
        while self.iscomparition():
            self.put_code(self.curToken.value)
            self.next()
            if id is not None:
                if check and self.checkToken(TokenType.QSM):
                    self._panik(f"Unexpected '?' at line: {self.lexer.get_line()}")
                if self.checkToken(TokenType.QSM):
                    check = True
                    self.put_code(id)
                    self.next()
                else:
                    self.expr()
            else:
                self.expr()
            self.checkBracket()
        self.parentId = lastParent


    # expr ::= term ( "-" | "+" ) term | term | func
    def expr(self, put_code=True):
        self.logger += "EXPRESSION\n"
        # Check first close bracket
        if self.checkToken(TokenType.CBRACKET):
            self._panik("Unexpected ')'")
        self.put_node("expr")
        lastParent = self.parentId
        self.parentId = self.treeId
        self.checkBracket()
        # Check using function
        if self.curToken.value in self.funcList or\
                self.curToken.value in self.defaultFunc:
            self.visitedFunc.add(self.curToken.value)
            self.put_node(self.curToken.value)
            self.put_node('(')
            if self.curToken.value in self.defaultFunc:
                self.put_code(f'default.{self.curToken.value}(')
                numParams = self.defaultFunc[self.curToken.value]
            else:
                self.put_code(f'{self.curToken.value}(')
                numParams = self.funcList[self.curToken.value]
            self.next()
            self.checkFunc(numParams)
        else:
            self.term(put_code)
        self.checkBracket()
        while self.checkToken(TokenType.PLUS) or \
                self.checkToken(TokenType.MINUS):
            self.put_node(self.curToken.value)
            # Put code in file or temp
            if put_code: 
                self.put_code(self.curToken.value)
            else: self.writter.put_temp(self.curToken.value)
            self.next()
            self.checkBracket()
            # Check using function
            if self.curToken.value in self.funcList or\
                    self.curToken.value in self.defaultFunc:
                if self.curToken.value in self.defaultFunc:
                    self.visitedFunc.add(self.curToken.value)
                    self.put_code(f'default.{self.curToken.value}(')
                    numParams = self.defaultFunc[self.curToken.value]
                else:
                    self.put_code(f'{self.curToken.value}(')
                    numParams = self.funcList[self.curToken.value]
                self.next()
                self.checkFunc(numParams)
            else:
                self.term(put_code)
        self.parentId = lastParent

    # term ::= primary | primary ( "/" | "*" ) primary
    def term(self, put_code=True):
        self.logger += "TERM\n"
        self.put_node("term")
        lastParent = self.parentId
        self.parentId = self.treeId
        self.primary(put_code)
        self.checkBracket()
        while self.checkToken(TokenType.SLASH) or \
                self.checkToken(TokenType.STAR):
            # Put code in file or temp
            self.put_node(self.curToken.value)
            if put_code: 
                self.put_code(self.curToken.value)
            else: self.writter.put_temp(self.curToken.value)
            self.next()
            self.checkBracket()
            self.primary(put_code)
            self.checkBracket()
        self.parentId = lastParent

    # PRIMARY ::= number | id
    def primary(self, put_code=True):
        self.logger += f"PRIMARY ({self.curToken.value})\n"
        self.put_node(f"PRIMARY ({self.curToken.value})")
        # Put code in file or temp
        if put_code:
            if self.curToken.value in self.defaultConst:
                self.put_code(f"default.{self.curToken.value}")
                self.usedConst.add(self.curToken.value)
            else:
                self.put_code(self.curToken.value)
        else: self.writter.put_temp(self.curToken.value)
        if self.checkToken(TokenType.NUMBER):
            self.next()
        elif self.checkToken(TokenType.ID):
            # check if parameter is declared
            if not self.curScope.checkId(self.curToken.value) and\
                    not self.curScope.checkConst(self.curToken.value):
                self._panik(f"Undeclared parameter at line {self.lexer.get_line()}: {self.curToken.value}")
            self.next()
        elif self.curScope.checkConst(self.curToken.value):
            self.next()
        else:
            self._panik(f"Expected a number or an identity at line {self.lexer.get_line()}: {self.curToken.value}")

    # nl ::= '\n' +
    def nl(self, put_line=True):
        if not (self.checkcurios(TokenType.EIF) or\
                self.checkcurios(TokenType.EOF) or\
                self.checkcurios(TokenType.ESW) or\
                self.checkcurios(TokenType.ESO) or\
                self.checkcurios(TokenType.EWH)):
            # self.lexer.get_line() += 1
            self.logger += "NEWLINE\n"
            if put_line: self.put_code("\n")
        self.match(TokenType.NEWLINE)
        self.put_node("NEWLINE")
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
            self.put_code('(')
            self.put_node('(')
            self.bCounter += 1
            self.next()
        while self.checkToken(TokenType.CBRACKET):
            self.put_code(')')
            self.put_node(')')
            self.bCounter -= 1
            self.next()

    def checkFunc(self, numParams):
        self.match(TokenType.OBRACKET)
        self.bCounter += 1
        for i in range(numParams):
            self.expr()
            if i != numParams -1 :
                self.match(TokenType.SEPARATOR)
                self.put_code(',')

    def checkId(self, id):
        return id in self.curScope.checkId(id)

    def check_const(self, id):
        return id in self.curScope.checkConst(id)

    def put_code(self, code):
        self.writter.put_code(code, self.inFunc)

    def create_scope(self, name='inner'):
        if self.inFunc: name = 'func-' + name
        parentScope = self.curScope
        self.curScope = Inner(parentId=self.curScope.idList+self.curScope.parentId,\
             parentConst=self.curScope.constId+self.curScope.parentConst, name=name)
        return parentScope

    def put_node(self, value):
        self.tree.putNode(self.parentId, self.treeId+1, value)
        self.treeId += 1

    # Throw Error
    def _panik(self, msg):
        print(self.logger)
        print(self.curScope.idList)
        sys.exit(f"ABORT ABORT!\n PARSER paniked! {msg}")

    # Build logger
    def makeLog(self):
        import os
        if not os.path.exists('temp'):
            os.makedirs('temp')
        self.lexer.makeLog()
        with open('temp/.parser','w+') as f:
            f.write(self.logger)
        
        self.tree.draw()
        self.curScope.drawTable()
