from graphviz import Digraph
class Tree:
    def __init__(self):
        self.dot = Digraph(graph_attr={'splines':'false', 'ranksep':'1'})
        self.dot.node('0','PROGRAM')

    def putNode(self, parent, key, children):
        key = str(key)
        parent = str(parent)
        self.dot.node(key, children)
        self.dot.edge(parent, key)
        

    def draw(self):
        # print(self.dot.source)
        self.dot.render('temp/parseTree.gv',view=True)
