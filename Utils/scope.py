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

    def drawTable(self):
        from graphviz import Digraph

        table = Digraph('structs', filename='structs_revisited.gv',
            node_attr={'shape': 'none'})

        self.getContent(-1,0,table)
        # print(table.source)
        table.render('temp/symboltable.gv',view=True)


    def getContent(self, parent, scope, table):
        content = '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">'
        content += '<TR><TD>ID</TD><TD>Scope</TD><TD>ScopeId</TD></TR>'

        for id in self.idList:
            content += f'<TR><TD>{id}</TD><TD>{self.name}</TD><TD>{scope}</TD></TR>'
        for id in self.constId:
            content += f'<TR><TD>{id}</TD><TD>{self.name}-const</TD><TD>{scope}</TD></TR>'
        content += '</TABLE>>'
        table.node(str(scope), content)
        if parent != -1:
            table.edge(str(parent), str(scope))
        parent = scope
        for inner in self.inner:
            if len(inner.idList) == 0 and len(inner.constId) == 0:
                continue
            scope += 1
            scope = inner.getContent(parent, scope, table)
        return scope


