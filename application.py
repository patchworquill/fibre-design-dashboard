# Dash Cytoscape Dashboard
# Patrick Wilkie
# 2022-05-24

import base64
import datetime
import io

import networkx as nx
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

import dash
from dash import html, dash_table, dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc


cyto.load_extra_layouts()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], meta_tags=[
                {"name": "viewport", "content": "width=device-width"}],)

# file = 'K:\Clients\AFL - AFL\\2021\\015 - Oakridge AB - OKRG\OKRG 1031B\DFD\(Fibre Data) OKRG 1031B.xlsx'
file = './(Fibre Data) OKRG 1031B.xlsx'
nodes_df = pd.read_excel(file, sheet_name="Node", header=0)

edges_df = pd.read_excel(file, sheet_name="Wire", header=0)
G = nx.from_pandas_edgelist(edges_df, "Start", "End", edge_attr=[
                            "Cap", "CableActivity"], edge_key="End")
cy = nx.readwrite.json_graph.cytoscape_data(G)

# Custom Node Labelling
# Slice NODES Dataframe and convert properties to strings for display
# node_keys = ["NODE", 'Struc', 'SpliceNo', 'SheetNo',
#              'FCP', 'Type', 'SSS', 'Live', 'SPARE']
# slice_node_label = nodes_df[node_keys]
# names = []
# for node in list(slice_node_label.index):
#     this_str = '\n'.join(str(x)
#                          for x in slice_node_label.values.tolist()[node])
#     this_str = this_str.replace("nan", '')
#     names.append(this_str)

# names = list(nodes_df["NODE"])

# Create the Nodes List
# print(nodes_df.NODE)
NODES_LIST = list(
    x for x in nodes_df['Struc'].unique() if pd.isnull(x) == False)
nodes_cy = [{'data': {'id': x, 'label': x}} for x in list(nodes_df.NODE)]

colors = {'Live': 'lightpink',
          'Spare': 'khaki',
          'Reserved': 'lightblue'}


# Allocation Plot
fig = go.Figure(data=[
                go.Bar(
                    name="Live", x=nodes_df["Struc"], y=nodes_df["Live"], marker_color=colors['Live']),
                go.Bar(
                    name="Spare", x=nodes_df["Struc"], y=nodes_df["SPARE"], marker_color=colors['Spare']),
                go.Bar(
                    name="RSVD", x=nodes_df["Struc"], y=nodes_df["RSVD"], marker_color=colors['Reserved']),
                go.Bar(
                    name="Spare2", x=nodes_df["Struc"], y=nodes_df["SPARE2"], marker_color=colors['Spare']),
                go.Bar(
                    name="RSVD2", x=nodes_df["Struc"], y=nodes_df["RSVD2"], marker_color=colors['Reserved']),
                go.Bar(
                    name="Spare3", x=nodes_df["Struc"], y=nodes_df["SPARE3"], marker_color=colors['Spare'])
                ])
fig.update_layout(barmode='stack', title='Fiber Allocation')

# Capacity Plot
fig2 = go.Figure(data=[
    go.Bar(
        name="Capacity", x=edges_df["End"], y=edges_df["Cap"]),  # marker_color=colors['Live']
])
fig2.update_layout(barmode='stack', title='Fiber Capacity')

#################################################
#
#
#                 BOOTSTRAP LAYOUT
#
#
#################################################

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            # TODO: Implement File Uploading
            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop ',
                        html.A('Files')
                    ]),
                    style={
                        'width': '100%',
                        # 'height': '60px',
                        # 'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    # Allow multiple files to be uploaded
                    # multiple=True
                ),
            ]),
        ], width=2,
        ),
        dbc.Col([
            html.Div(id='output-data-upload'),
        ]),
        dbc.Col([
            html.H1("OKRG", id="project_name")
        ]),
        dbc.Col([
            html.H1("1013B", id="fsa_name")
        ]),
        dbc.Col([
            html.H4("NODES"),
            html.H4("X", id="node_count")
        ]),
        dbc.Col([
            html.H4("LONGEST BRANCH")
        ]),
        dbc.Col([
            html.H1("5")
        ]),
        dbc.Col([
            html.H1("5")
        ]),
        dbc.Col([
            html.H1("5")
        ]),
        dbc.Col([
            html.H1("5")
        ]),
        dbc.Col([
            html.H1("5")
        ]),
    ]),

    #############
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.H3("Layout"),
                ],
                    width=3,  # TODO: This is statically coded, will overlap longer text
                ),
                dbc.Col([
                    dcc.Dropdown(
                        options={item: item.capitalize() for item in ["random", "preset", "circle", "concentric", "grid",
                                                                      "breadthfirst", "cose", "cola", "euler", "spread", "dagre", "klay"]},  # "close-bilkent",
                        value='klay',
                        id='layout-selector',
                        clearable=False
                    ),
                ]),
            ]),

            dbc.Row([cyto.Cytoscape(
                id='cytoscape-fsa',
                # autoungrabify=True,
                # minZoom=1,
                # maxZoom=1,
                responsive=True,
                layout={'name': 'klay'},  # dagre #breadthfirst #klay #cola
                style={'width': '100%', 'height': '500px',
                    'text-overflow-wrap': 'anywhere', 'text-sizing': 'relative'},
                elements={'nodes': nodes_cy, 'edges': cy['elements']['edges']},
            )
            ]),
        ],
            id='cytograph',
            width=4,
        ),

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Button("Calculate FCP Number",
                                   id='fcp-button', color="muted"),
                    ]),
                ],
                    width=2,
                ),
                dbc.Col([
                    dbc.Row([
                        dbc.Button("Calculate Range",
                                   id='range-button', color="muted"),
                    ]),

                ],
                    width=2,
                ),
                dbc.Col([
                    dbc.Row([
                        dbc.Button("Calculate Activity Number",
                                   id='activity-button', color="primary"),
                    ]),

                ],
                    width=2,
                ),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                            # text_color="primary", "secondary", "success", "warning", "danger", "info", "dark", "black", "muted"
                            dbc.Badge('4', pill=True, id="fcp-badge",
                                      color="success", className="ms-1"),
                            ]),
                ],
                width=2,
                ),
                dbc.Col([
                    dbc.Row([
                        # text_color="primary", "secondary", "success", "warning", "danger", "info", "dark", "black", "muted"
                        dbc.Badge('4', pill=True, id="range-badge",
                                  color="success", className="ms-1"),
                    ]),
                ],
                width=2,
                ),
                dbc.Col([
                    dbc.Row([
                        # text_color="primary", "secondary", "success", "warning", "danger", "info", "dark", "black", "muted"
                        dbc.Badge('4', pill=True, id="activity-badge",
                                  color="success", className="ms-1"),
                    ]),
                ],
                width=2,
                ),
            ],
                id="calculation-status",
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dcc.Store(id='memory-output'),
                    ]),
                    dbc.Row([
                        dcc.Dropdown(NODES_LIST,
                                     value=NODES_LIST,  # Initialization
                                     id='node-selector',
                                     multi=True),
                    ]),
                ],
                    width=3,
                ),
                dbc.Col([
                    dcc.RadioItems(
                                    id="node-selector-radio",
                                    options=[
                                        {"label": "All ", "value": "all"},
                                        {"label": "SB only ", "value": "active"},
                                        {"label": "Customize ", "value": "custom"},
                                    ],
                                    value="all",
                                    labelStyle={"display": "inline-block"},
                                    className="dcc_control",
                                ),
                ],
                ),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dash_table.DataTable(
                            id='memory-table',
                            columns=[{'name': i, 'id': i}
                                     for i in nodes_df.columns]
                        ),
                    ])
                ],
                ),
            ],
            ),
        ],
        ),
    ],),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='allocation-graph',
                figure=fig
            )
        ]),
        dbc.Col([
            dcc.Graph(
                id='allocation-graph2',
                figure=fig2
            )
        ]),
    ],
        id="bar-div",
        className='four columns'
    ),

    html.Div([
        html.Div(id='empty-div', children='')
    ],
        className='one columns'
    ),

],
    id='mainContainer',
    style={"display": "flex", "flex-direction": "column", "width": "100%"},
    fluid=True,
)

#################################################
#
#
#                   CALLBACKS
#
#
#################################################


@app.callback(Output('cytoscape-fsa', 'layout'),
              Input('layout-selector', 'value'))
def update_layout(layout_value):
    # print(layout_value)
    return {
        'name': layout_value,
        'animate': True
    }


# @app.callback(Output('memory-table', 'data'),  # memory-output
#               Input('node-selector', 'value'))
# def filter_nodes(nodes_selected):
#     if not nodes_selected:
#         # Return all the rows on initial load/no country selected.
#         return nodes_df.to_dict('records')

#     # .query('node in @nodes_selected')
#     filtered = nodes_df[nodes_df['Struc'].isin(list(nodes_selected))]

#     return filtered.to_dict('records')


# @app.callback(Output('node-selector', 'value'),
#               Input('cytoscape-fsa', 'tapNodeData'),  # tapNodeData
#               Input('node-selector', 'value')
#               )
# def on_data_set_table(tapNodeData, nodeList):
#     print("\n\n\n")
#     print(nodeList)
#     if nodeList is None:
#         return []

#     if tapNodeData is None:
#         print(tapNodeData)
#         raise PreventUpdate
#     else:
#         # print("TABLE DATA:", tableData)
#         print("ID:", tapNodeData["id"], type(tapNodeData["id"]))
#         data = nodes_df.at[int(tapNodeData["id"]), "Struc"]
#         print(data, type(data))
#         print('NODELIST', nodeList, type(nodeList))
#         nodeList.append(data)

#     return nodeList

# Radio -> multi
@app.callback(
    Output("node-selector", "value"), [
        Input("node-selector-radio", "value")]
)
def display_status(selector):
    if selector == "all":
        return list(NODES_LIST)
    # elif selector == "active":
    #     return ["AC"]
    return []

@app.callback(Output('memory-table', 'data'),
              Input('cytoscape-fsa', 'tapNodeData'),
            #   Input('cytoscape-fsa', 'selectedNodeData'),
              Input('node-selector','value')  # tapNodeData
              )
def on_data_set_table(tapNodeData, nodeList):
    if tapNodeData is None:
        raise PreventUpdate
    else:
        data = nodes_df.at[int(tapNodeData["id"]), "Struc"]
        # print(data, type(data))
        nodeList.append(data)

    filtered = nodes_df[nodes_df['Struc'].isin(list(nodeList))]

    return filtered.to_dict('records')


@app.callback(
    # Output('Live', '?'),
    Output('empty-div', 'children'),
    Input('cytoscape-fsa', 'mouseoverNodeData'),
    Input('cytoscape-fsa', 'mouseoverEdgeData'),
    Input('cytoscape-fsa', 'tapEdgeData'),
    Input('cytoscape-fsa', 'tapNodeData'),
    Input('cytoscape-fsa', 'selectedNodeData')
)
def update_layout(mouse_on_node, mouse_on_edge, tap_edge, tap_node, snd):
    # print("Mouse on Node: {}".format(mouse_on_node))
    # print("Mouse on Edge: {}".format(mouse_on_edge))
    # print("Tapped Edge: {}".format(tap_edge))
    # print("Tapped Node: {}".format(tap_node))
    # print("------------------------------------------------------------")
    # print("All selected Nodes: {}".format(snd))
    # print("------------------------------------------------------------")

    return ''  # 'see print statement for nodes and edges selected.'


@app.callback(
    Output("range-badge", "children"),
    Input("range-button", "n_clicks")
)
def on_button_click(n):
    if n is None:
        return "Not clicked."
    else:
        return f"Clicked {n} times."


@app.callback(
    Output("activity-badge", "children"),
    Input("activity-button", "n_clicks")
)
def on_button_click(n):
    if n is None:
        return "Not clicked."
    else:
        return f"Clicked {n} times."


@app.callback(
    Output("fcp-badge", "children"),
    Input("fcp-button", "n_clicks")
)
def on_button_click(n):
    if n is None:
        return "Not clicked."
    else:
        return f"Clicked {n} times."



# TODO: Filter Barchart Graph Object to highlight current node, displaying the LIVE and SPARE count for that node.
# @app.callback(
#     Output('allocation-graph', 'fig'),
#     Input('cytoscape-fsa', 'mouseoverNodeData'),
# )
# def update_layout(mouse_on_node):
#     fig.update_layout(barmode='stack', title='Fiber Allocation')
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__ == '__main__':
    app.run_server(debug=True)
