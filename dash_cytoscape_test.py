# Dash Cytoscape Attempt

# Dash 1.2 import statements
# import dash_html_components as html
# import dash_core_components as dcc

import dash
import dash_cytoscape as cyto
from dash import html
from dash import dcc
from dash.dependencies import Output, Input
import networkx as nx
import json
import pandas as pd
import plotly.express as px

cyto.load_extra_layouts()

app = dash.Dash(__name__)

file = 'K:\Clients\AFL - AFL\\2021\\015 - Oakridge AB - OKRG\OKRG 1031B\DFD\(Fibre Data) OKRG 1031B.xlsx'
nodes_df = pd.read_excel(file, sheet_name="Node", header=0)

edges_df = pd.read_excel(file, sheet_name="Wire", header=0)
G = nx.from_pandas_edgelist(edges_df, "Start", "End", edge_attr=[
                            "Cap", "CableActivity"], edge_key="End")
cy = nx.readwrite.json_graph.cytoscape_data(G)

# Slice NODES Dataframe and convert properties to strings for display
node_keys = ["NODE", 'Struc', 'SpliceNo', 'SheetNo',
             'FCP', 'Type', 'SSS', 'Live', 'SPARE']
slice_node_label = nodes_df[node_keys]
names = []
for node in list(slice_node_label.index):
    this_str = '\n'.join(str(x)
                         for x in slice_node_label.values.tolist()[node])
    this_str = this_str.replace("nan", '')
    names.append(this_str)

# Create the Nodes List
nodes_cy = [{'data': {'id': x, 'label': names[x]}} for x in nodes_df.NODE]

app.layout = html.Div([
    html.Div([

        dcc.Dropdown(
            options = {item: item.capitalize() for item in ["random","preset","circle","concentric","grid","breadthfirst","cose","cola","euler","spread","dagre","klay"]}, #"close-bilkent",
            value='cola',
            id='layout-selector',
            clearable=False
        ),

        html.Br(),

        cyto.Cytoscape(
            id='cytoscape-fsa',
            # autoungrabify=True,
            # minZoom=0.2,
            # maxZoom=1,
            responsive=True,
            layout={'name': 'cose'},  # dagre #breadthfirst #klay #cola
            style={'width': '100%', 'height': '500px', 'text-wrap': 'wrap', 'text-sizing': 'relative'},
            elements={'nodes': nodes_cy, 'edges': cy['elements']['edges']},
            stylesheet=[
            # Group selectors
            {
                'selector': 'nodes',
                'style': {
                    'content': 'data(label)'
                }
            },

            # Class selectors
            {
                'selector': '.red',
                'style': {
                    'background-color': 'red',
                    'line-color': 'red'
                }
            },
            {
                'selector': '.triangle',
                'style': {
                    'shape': 'triangle'
                }
            }
        ]
        )
    ], className='six-columns'),

    html.Br(),

    html.Div([
        html.Div(id='empty-div', children='')
    ], className='one column'),

    html.Div([
        dcc.Graph(id='my-graph', figure=px.bar(nodes_df, x='NODE', y='Live'))
    ], className='two columns'),

], className='row')

@app.callback(Output('cytoscape-fsa', 'layout'),
              Input('layout-selector', 'value'))
def update_layout(layout_value):
        print(layout_value)
        return {
            'name': layout_value,
            'animate': True
        }

@app.callback(
    Output('empty-div', 'children'),
    Input('cytoscape-fsa', 'mouseoverNodeData'),
    Input('cytoscape-fsa','mouseoverEdgeData'),
    Input('cytoscape-fsa','tapEdgeData'),
    Input('cytoscape-fsa','tapNodeData'),
    Input('cytoscape-fsa','selectedNodeData')
)
def update_layout(mouse_on_node, mouse_on_edge, tap_edge, tap_node, snd):
    print("Mouse on Node: {}".format(mouse_on_node))
    print("Mouse on Edge: {}".format(mouse_on_edge))
    print("Tapped Edge: {}".format(tap_edge))
    print("Tapped Node: {}".format(tap_node))
    print("------------------------------------------------------------")
    print("All selected Nodes: {}".format(snd))
    print("------------------------------------------------------------")

    return 'see print statement for nodes and edges selected.'


# @app.callback(
#     Output('my-graph','figure'),
#     Input('cytoscape-fsa','tapNodeData'),
# )
# def update_nodes(data):
#     if data is None:
#         return dash.no_update
#     else:
#         nodesy = df.copy()
#         nodesy.loc[nodesy.name == data['label'], 'color'] = "yellow"
#         fig = px.bar(nodes_df, x='NODE', y='Live')
#         fig.update_traces(marker={'color': nodesy['Struc']})
#         return fig

# Read JSON
# json_file = 'K:\Clients\AFL - AFL\\2021\\015 - Oakridge AB - OKRG\OKRG 1031B\DFD\Py\cy_1031B.json'
# with open(json_file) as f:
#     cy = json.load(f)
#     f.close()

if __name__ == '__main__':
    app.run_server(debug=True)
