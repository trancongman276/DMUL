from tokentype import TokenType

class Writer:
    def __init__(self, path):
        self.lib = "from default import default\n"
        self.func = ""
        self.code = ""
        self.temp = ""
        self.path = path
    
    def put_code(self, code):
        self.code += code

    def put_temp(self, code):
        self.temp += code

    def pop_temp(self):
        self.code += self.temp
        self.temp = ""

    def put_func_code(self, code):
        self.func += code

    def put_func_line(self, code):
        self.func += code + '\n'

    def write_file(self):
        with open(self.path, 'w') as f:
            f.write(self.lib + self.func + self.code)
