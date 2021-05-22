from graphviz import Digraph

s = Digraph('structs', filename='structs_revisited.gv',
            node_attr={'shape': 'none'})
s.node('set1','<\
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">\
        <TR>\
            <TD>Blue Crosses</TD>\
            <TD>Square</TD>\
        </TR>\
        <TR>\
            <TD>B1</TD>\
            <TD PORT="b1">Left</TD>\
        </TR>\
        <TR>\
            <TD>B2</TD>\
            <TD PORT="b2">Left</TD>\
        </TR>\
        <TR>\
            <TD>Right</TD>\
            <TD PORT="b3">Right</TD>\
        </TR>\
        <TR>\
            <TD>B4</TD>\
            <TD>Left</TD>\
        </TR>\
    </TABLE>>')
s.node('set2','<\
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">\
        <TR>\
            <TD>Blue Crosses</TD>\
            <TD>Coordinates</TD>\
        </TR>\
        <TR>\
            <TD PORT="b1">B1</TD>\
            <TD>(1, 1)</TD>\
        </TR>\
        <TR>\
            <TD PORT="b2">B2</TD>\
            <TD>(2, 2)</TD>\
        </TR>\
        <TR>\
            <TD PORT="b3">B3</TD>\
            <TD>(4, 2)</TD>\
        </TR>\
    </TABLE>>')

s.edges([('set1', 'set2')])

s.view()