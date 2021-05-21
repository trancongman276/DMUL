class Writer:
    def __init__(self, path):
        self.lib = "from default import default\n"
        self.func = ""
        self.code = ""
        self.temp = ""
        self.path = path
    
    def put_code(self, code, isFunc=False):
        if isFunc: self.func += code
        else: self.code += code

    def put_temp(self, code):
        self.temp += code

    def pop_temp(self):
        self.code += self.temp
        self.temp = ""

    def write_file(self):
        with open(self.path, 'w') as f:
            f.write(self.lib + self.func + self.code)
