from tokentype import TokenType
from semantictype import SemanticType
from datatype import DataType

DMUL_Symboltable = []
stack = []
class SymbolTable:
    
    def __init__(self, lexeme, tokentype, semantictype, datatype, value, scope):
        self.lexeme = lexeme
        self.tokentype = tokentype
        self.semantictype = semantictype
        self.datatype = datatype
        self.value = value
        self.scope = scope

        self.update()
        self.insert()
        
    def insert(self):
        if self.lookup() is False:
            DMUL_Symboltable.append(self)
            stack.append(self)
    
    def update(self):
        if(100 < self.semantictype < 200):
            self.semantictype = SemanticType.stkeyword.name
            self.datatype = DataType.dtnone.name
            self.value = None

        elif(200 <self.semantictype < 300):
             self.semantictype = SemanticType.stoperator.name
             self.datatype = DataType.dtnone.name
             self.value = None

        elif(self.semantictype == 1) or (self.semantictype == 3):
             self.semantictype = SemanticType.stconstant.name
             
             if(self.semantictype == 1): self.datatype = DataType.dtinteger.name
             else: self.datatype = DataType.dtstring.name

        elif(self.semantictype == 2):
             self.semantictype = SemanticType.stliteral.name
             if (self.datatype == 1): self.datatype = DataType.dtinteger.name
             elif (self.datatype == 3): self.datatype = DataType.dtstring.name
             else: self.datatype = DataType.dtunknow.name


        elif(self.semantictype == -1) or (self.semantictype == 0):
             self.semantictype = SemanticType.stprogram.name
             self.datatype = DataType.dtprogram.name

        else: 
            self.semantictype = SemanticType.stunknow.name
            self.datatype = DataType.dtunknow.name

    def printSymbolTable():
        print("+-----------------------The symbol table is:----------------------+")
        print("| Lexeme | Token-Type | Semantic-Type | Data-Type | Value | Scope |")
        print("+-----------------------------------------------------------------+")
        for i in range(0, len(DMUL_Symboltable)):    
            print("|",DMUL_Symboltable[i].lexeme, "|", DMUL_Symboltable[i].tokentype, "|", DMUL_Symboltable[i].semantictype, "|", DMUL_Symboltable[i].datatype, "|", DMUL_Symboltable[i].value, "|", DMUL_Symboltable[i].scope)    
        print("+-----------------------------------------------------------------+")


    def isEmptyStack():
        return len(stack)

    def pop():
        return stack.pop()
    #    i = len(DMUL_Symboltable) - 1
    #    print("THE POP ARRAY: ", i)
    #    print(DMUL_Symboltable[i].lexeme, "|", DMUL_Symboltable[i].tokentype, "|", DMUL_Symboltable[i].semantictype, "|", DMUL_Symboltable[i].datatype, "|", DMUL_Symboltable[i].value, "|", DMUL_Symboltable[i].scope)
    #    return DMUL_Symboltable[i]


    def modify(self,token):
        if self.semantictype == SemanticType.stliteral.name:
            if(token.kind.value == 1):
                self.datatype = DataType.dtinteger.name
                self.value = token.value
            elif(token.kind.value == 3):
                self.datatype = DataType.dtstring.name
                self.value = token.value
            elif(token.kind.value == 2):
                self.datatype = self.lookupValue(token.value)
                self.value = token.value
        
        # print("THE MODIFY VER VALUE")
        # print(self.lexeme, "|", self.tokentype, "|", self.semantictype, "|", self.datatype, "|", self.value, "|", self.scope)

    def lookup(self):
        exist = 0
        for i in range(0, len(DMUL_Symboltable)):
            if self.lexeme==DMUL_Symboltable[i].lexeme:
                exist = 1
        if exist == 1: return True
        else: return False
    
    def lookupValue(self, tkvalue):
        dtype = DataType.dtunknow.name
        for i in range(0, len(DMUL_Symboltable)):
            if DMUL_Symboltable[i].lexeme==tkvalue:
                dtype = DMUL_Symboltable[i].datatype
        return dtype
