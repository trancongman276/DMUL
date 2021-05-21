class Inner:
    def __init__(self, parentId, parentConst, name):
        self.name = name
        self.idList = []
        self.constId = []
        self.inner = []
        self.parentConst = parentConst
        self.parentId = parentId

    def checkId(self, id):
        return id in self.parentId or\
                id in self.idList
        
    def checkConst(self, id):
        return id in self.parentConst or\
                id in self.constId

    def buildTable(self, scope, tabulator):
        content = ""

        for id in self.idList:
            content += f"{tabulator(id)}{tabulator(self.name)}{tabulator(str(scope))}\n"

        for id in self.constId:
            content += f"{tabulator(id)}{tabulator(self.name+'-const')}{tabulator(str(scope))}\n"
        
        for inner in self.inner:
            if len(inner.idList) == 0 and len(inner.constId) == 0:
                continue
            scope += 1
            content += inner.buildTable(scope, tabulator)
        
        return content


