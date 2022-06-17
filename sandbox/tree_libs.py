## Treelib
from treelib import Node, Tree

tree = Tree()
tree.create_node("CEO","CEO") #root
tree.create_node("VP_1","VP_1",parent="CEO" )
tree.create_node("VP_2","VP_2",parent="CEO" )
tree.create_node("GM_1","GM_1",parent="VP_1" )
tree.create_node("GM_2","GM_2",parent="VP_2" )

## Anytree
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
ceo = Node("CEO") #root
vp_1 = Node("VP_1", parent=ceo)
vp_2 = Node("VP_2", parent=ceo)
gm_1 = Node("GM_1", parent=vp_1)
gm_2 = Node("GM_2", parent=vp_2)
m_1 = Node("M_1", parent=gm_2)
DotExporter(ceo).to_picture("ceo.png", )