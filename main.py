from DMUL_Writer import Writer
from DMUL_Lexer import Lexer
from DMUL_Parser import Parser
import sys


# if len(sys.argv) != 2:
#     sys.exit("Required source file")    
with open('test.dmul', 'r') as file:
    print("DMUL compiler is running...")
    code = file.read()
    writer = Writer('out.py')
    parser = Parser(Lexer(code), writer)
    parser.program()
    print("Finished!")

from subprocess import call
call(['python','out.py'])