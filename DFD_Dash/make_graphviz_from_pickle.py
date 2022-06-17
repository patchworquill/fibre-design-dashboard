import pydot
import matplotlib.pyplot as plt
import networkx as nx
import pydot_ng as pydot
import graphviz
from networkx.drawing.nx_pydot import graphviz_layout

OUTPATH = 'Data/1142A/'
data_path = OUTPATH+'out.pkl'
G = nx.read_gpickle(data_path)
# DG = nx.DiGraph(G)

nx.draw(G, with_labels=True, font_weight='bold')
# nx.draw_networkx_nodes(G, pos)
# nx.draw_networkx_edges(G, pos)
plt.show()

pos = nx.nx_pydot.graphviz_layout(G)
# pos = nx.nx_agraph.pygraphviz_layout(G, prog="dot", root=G.nodes['FDH']) # Requires pygraphviz
nx.draw(G, pos=pos)
plt.show()
nx.nx_agraph.write_dot(G, OUTPATH+"out.dot")

## Convert NetworkX to PyDot
# Use a simplified graph with less attributes for now:
# G = nx.from_pandas_edgelist(edges_df, edges_df.columns.tolist()[0], edges_df.columns.tolist()[1], edge_key=edges_df.columns.tolist()[1])

graph = nx.drawing.nx_pydot.to_pydot(G)

graph = pydot.Dot()

# Re-create the node-dictionary by keys
# Re-create the edge-dictionary by keys
# Format the node_label string to use

G.nodes[node]

try:
    node_label = 'Ok lets try Struc: {Struc} Splice: {Splice} Count: {LiveCount} Spare: {SpareCount}'
    node_label.format_map(G.nodes[node])
except KeyError as ke:
    print("There's a missing key:", ke)

for node in G.nodes:
    try:
        
        node_label = """<<table border='0' cellspacing='0'>
                        <tr><td port='sheet'    border='0' bgcolor='white'>{Sheet}</td></tr>
                        <tr><td port='splice'   border='0'><b>{Splice}</b></td></tr>
                        <tr><td port='struc'    border='0'></td>{node}</tr>
                        <tr><td port='fcp'      border='0'>{FCP}</td></tr>
                        <tr><td port='stype'    border='0'><b>{SType}</b></td></tr>
                        <tr><td port='sss'      border='0' bgcolor='#FFC000'>{SSS}</td></tr>
                        <tr><td port='fibre'    border='0' bgcolor='#FFCCFF'>{LiveCount}</td></tr>
                        <tr><td port='spare'    border='0' bgcolor='#FFFF00'>{SpareCount}</td></tr>
                        <tr><td port='rsvd'     border='0' bgcolor='#E26B0A'>{RSVD1}</td></tr>
                        <tr><td port='spare2'     border='0' bgcolor='#FFFF00'>{Spare1}</td></tr>
                        <tr><td port='rsvd2'     border='0' bgcolor='#E26B0A'>{RSVD2}</td></tr>
                        <tr><td port='spare3'     border='0' bgcolor='#FFFF00'>{Spare2}</td></tr>
                    <tr><td port='spl_ac'    border='0' bgcolor='white'>"{SpliceActivity}</td></tr>
            </table>>""".format_map(G.nodes[node])
        graph.add_node(pydot.Node(str(node), shape="record", label=node_label))
        print(G.nodes[node])
    except KeyError as ke:
        graph.add_node(pydot.Node(str(node), shape="record"))

# Add Edges
for edge in G.edges:
    try:
        edge_label = "{CableActivity}\n{Capacity}\n{FibreAllocation}\n{DeadRange}".format_map(G.edges[edge])
        graph.add_edge(pydot.Edge(str(edge[0]), str(edge[1]), label=edge_label))
        print(G.edges[edge])
    except KeyError as ke:
        graph.add_edge(pydot.Edge(str(edge[0]), str(edge[1])))

## Style the Graph
graph.set_strict(False)

# Output Graph
graph.write_png(OUTPATH+'output.png')
graph.write_pdf(OUTPATH+"output.pdf")
graph.to_string()
graph.write_dot(OUTPATH+"output_graphviz.dot")
graph.create_svg()

H = nx.convert_node_labels_to_integers(G, label_attribute='node_label')
H_layout = nx.nx_pydot.pydot_layout(G, prog='dot')
G_layout = {H.nodes[n]['node_label']: p for n, p in H_layout.items()}

graph.write_png(OUTPATH+'output.png')
graph.write_pdf(OUTPATH+"output.pdf")




## Load PyDot from .dot file
graphs = pydot.graph_from_dot_file('graphviz/fsa_1031B.dot')
graph = graphs[0]
G = nx.drawing.nx_pydot.from_pydot(graph)