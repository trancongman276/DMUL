from DMUL_Lexer import Lexer
from DMUL_Parser import Parser

with open('code.dmul', 'r') as file:
    print("DMUL compiler is running...")

    code = file.read()
    parser = Parser(Lexer(code))
    parser.program()

    print("Finished!")
