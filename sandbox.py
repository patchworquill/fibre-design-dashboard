######## Interesting Experiments
[n for n in nx.topological_generations(T)] 

leaf_nodes = [node for node in T.nodes() if T.in_degree(node)!=0 and T.out_degree(node)==0]
T.pred[child] # returns the parent node