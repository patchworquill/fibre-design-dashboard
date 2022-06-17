import pydot
import networkx as nx

graphs = pydot.graph_from_dot_file('graphviz/fsa_1031B.dot')
graph = graphs[0]

graph.write_png('output.png')
graph.write_pdf("output.pdf")
graph.create_svg()

G = nx.drawing.nx_pydot.from_pydot(graph)