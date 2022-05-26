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
import allocation as kt

cyto.load_extra_layouts()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], meta_tags=[
                {"name": "viewport", "content": "width=device-width"}],)

# file = 'K:\Clients\AFL - AFL\\2021\\015 - Oakridge AB - OKRG\OKRG 1031B\DFD\(Fibre Data) OKRG 1031B.xlsx'
file = './(Fibre Data) OKRG 1031B.xlsx'
nodes_df = pd.read_excel(file, sheet_name="Node", header=0)
# nodes_df["SpliceNo"]    = ["XX"]*len(nodes_df) # For testing
# nodes_df["FCP"]         = ["FCP"]*len(nodes_df) 
edges_df = pd.read_excel(file, sheet_name="Wire", header=0)
G = nx.from_pandas_edgelist(edges_df, "Start", "End", edge_attr=[
                            "Cap", "CableActivity"], edge_key="End")

cy = nx.readwrite.json_graph.cytoscape_data(G)

NODES_LIST = list(
    x for x in nodes_df['NODE'].unique() if pd.isnull(x) == False)
nodes_cy = [{'data': {'id': x, 'label': x}} for x in list(nodes_df.NODE)]

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
        name="Capacity", x=edges_df["End"], y=edges_df["Cap"], marker_color="lightgrey"),  # marker_color=colors['Live']
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
            dbc.Row([
            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop ',
                        html.A('Files')
                    ]),
                    style={
                        'width': '100%',
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
            ]),
            dbc.Row([html.P(str(file), id='filename')]),
            dbc.Row([
                html.Div(id='output-data-upload'),
            ]),
        ], width=2,
        ),
        dbc.Col([
            html.H4("COID"),
            html.H1("OKRG", id="project_name")
        ]),
        dbc.Col([
            html.H4("FSA"),
            html.H1("1013B", id="fsa_name")
        ]),
        dbc.Col([
            html.H4("Ⓣ NODES"),
            html.H2(html.Span(
                str(len(NODES_LIST)),
                id="tooltip-target",
                style={"cursor": "pointer"}, #"textDecoration": "underline"
            )),
            dbc.Tooltip(
                str(NODES_LIST),
                target="tooltip-target",
            ),
        ]),
        dbc.Col([
            html.H4("Ⓣ EDGES"),
            # html.H2(str(nx.number_of_edges(G))),
            html.H2(html.Span(
                str(nx.number_of_edges(G)),
                id="tooltip-target2",
                style={"cursor": "pointer"}, #"textDecoration": "underline"
            )),
            dbc.Tooltip(
                str(nx.edges(G)),
                target="tooltip-target2",
            ),
        ]),
        dbc.Col([
            html.H4("LIVE"),
            html.H2(str(nodes_df["Live"].sum()))
        ]),
        dbc.Col([
            html.H4("SPARE"),
            html.H2(str(nodes_df["SPARE"].sum()+nodes_df["SPARE2"].sum()+nodes_df["SPARE3"].sum())) #, "SPARE2", "SPARE3"
        ]),
        dbc.Col([
            html.H4("RSVD"),
            html.H2(str(nodes_df["RSVD"].sum()+nodes_df["RSVD2"].sum())) #, "SPARE2", "SPARE3"
        ]),
        dbc.Col([
            html.H4("DEGREE"),
            html.H2(html.Span("MAX"+str(len(nx.degree_histogram(G))-1), id="tooltip-target3")),
            dbc.Tooltip(
                str(nx.degree(G)),
                target="tooltip-target3",
            ),
        ]),
        # dbc.Col([
        #     html.H1("☉☉☉☉☉ 5"),
        #     html.H5(str())
        # ]),
        # dbc.Col([
        #     html.H1("5 ✇✇✇✇✇")
        # ]),
        dbc.Col([
            html.H2("CIVIL METERS")
        ]),
        dbc.Col([
            dbc.Button("SAVE", id='save-button', color="muted"),
        ]),
    ],
    id="info-text",
    style={"height": "8vh"}
    ),

    #############
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.H4("Fibre Layout"),
                ],
                    width=3, 
                ),
                dbc.Col([
                    dcc.Dropdown(
                        options={item: item.capitalize() for item in ["klay", "dagre", "cola", "euler", "spread", "circle", "concentric", "grid",
                                                                      "breadthfirst", "cose", "random"]},  # "close-bilkent",
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
            dbc.Row([
                html.Div([
                    html.Div(id='empty-div', children='')
                ],
                    className='one columns'
                ),
            ]),
        ],
            id='cytograph',
            width=4,
        ),

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Button("Calculate Activity Number",
                                   id='activity-button', color="primary"),
                    ]),

                ],
                    width=2,
                ),
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
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                            # text_color="primary", "secondary", "success", "warning", "danger", "info", "dark", "black", "muted"
                            dbc.Col([
                                dbc.Badge('4', pill=True, id="cable-activity-badge",
                                      color="muted", className="ms-1"),
                            ]),
                            dbc.Col([
                                dbc.Badge('4', pill=True, id="splice-activity-badge",
                                      color="muted", className="ms-1"),
                            ]),
                    ]),     
                ],
                width=2,
                ),
                dbc.Col([
                    dbc.Row([
                        # text_color="primary", "secondary", "success", "warning", "danger", "info", "dark", "black", "muted"
                        dbc.Badge('4', pill=True, id="fcp-badge",
                                  color="muted", className="ms-1"),
                    ]),
                ],
                width=2,
                ),
                dbc.Col([
                    dbc.Row([
                        # text_color="primary", "secondary", "success", "warning", "danger", "info", "dark", "black", "muted"
                        dbc.Badge('4', pill=True, id="range-badge",
                                  color="muted", className="ms-1"),
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
                    ]),
                    dbc.Row([
                        dcc.Dropdown(NODES_LIST,
                                     value=NODES_LIST,  # Initialization
                                     id='node-selector-dropdown',
                                     multi=True, 
                                     style={
                                        "overflow-y":"auto",
                                        "max-height": "10vh"
                                        }
                                    ),
                    ]),
                ],
                    width="100px",
                ),
                dbc.Col([
                    html.Div([
                        dash_table.DataTable(
                            id='memory-table',
                            # sort_action='native',
                            editable=True,
                            columns=[{'name': i, 'id': i}
                                     for i in nodes_df.columns],
                            fixed_rows={'headers': True},
                            style_table={
                                'overflowY': 'auto',
                                'height': '40vh',
                                'width': '60vw',
                                }
                        ),
                    ],
                    
                    )
                ],
                ),
            ],
            className="row h-40",
            id="data-table"
            ),
        ],
        style={"height": "60vh"}
        ),
    ],),

    #############s
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
        style={"height": "30vh"}
    ),

],
    id='mainContainer',
    style={"display": "flex", "flex-direction": "column", "width": "100%", "height": "100vh"},
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

@app.callback(Output('node-selector-dropdown', 'value'),
              Input('cytoscape-fsa', 'tapNodeData'),
              Input('cytoscape-fsa', 'selectedNodeData'),
              Input("node-selector-radio", "value")
              )
def on_graph_add_to_dropdown(tapNodeData, selectedNodeData, radioSelector):
    if radioSelector == "all":
        selected_list = NODES_LIST
    elif radioSelector == "active":
        selected_list = []
    else:
        selected_list = []
        for node in selectedNodeData:
            print(node)
            selected_list = nodes_df.at[nodes_df.index[nodes_df['NODE'] == int(node["id"])], "NODE"].tolist()
            selected_list.append() #nodes_df.at[int(node["id"]), "NODE"])
        # selected_list.append(nodes_df.at[nodes_df.index[nodes_df['NODE'] == (int(node["id"]))], "NODE"])
        print(selected_list)

    return selected_list


@app.callback(Output('memory-table', 'data'),
              Input('node-selector-dropdown','value')  # tapNodeData
              )
def on_data_set_table(nodeList):
    filtered = nodes_df[nodes_df['NODE'].isin(list(nodeList))]

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
    
    display_string = "Select Edge: {}".format(tap_edge)
    # display_string = str("Node id: " + tap_node["id"] 
    #             +"\nEdge id: " + tap_edge["id"] 
    #             + "\nCap:" + tap_edge["Cap"]
    #             + "\nCableActivity:" + tap_edge["CableActivity"]
    #             )

    return display_string  # 'see print statement for nodes and edges selected.'


@app.callback(
    Output("cable-activity-badge", "children"),
    Output("cable-activity-badge", "color"),
    Output("splice-activity-badge", "children"),
    Output("splice-activity-badge", "color"),
    Output("node-selector-radio", "value"),
    Output("activity-button", "color"),
    Output("fcp-button", "color"),
    Input("activity-button", "n_clicks")
)
def on_button_click(n):
    # clarify interface for these functions
    if not n:
        cable_text = "Not clicked."
        cable_flag = "muted"
        splice_text = "Not clicked."
        splice_flag = "muted"
        button_color = "primary"
        next_button = "muted"
    else:
        cable_status, cable_list = kt.cable_activities(G, edges_df)
        edges_df["CableActivity"] = cable_list
        cable_list = filter(None, cable_list)
        cable_text = str("CABLE")

        splice_status, splice_list = kt.splice_activities(G, nodes_df, cable_list)
        nodes_df["SpliceNo"] = splice_list
        splice_list = filter(None, splice_list)
        splice_text = "SPLICE"

        # TODO: insert these into the pandas dataframes and refresh
        
        if(cable_status):
            cable_flag = "success"
        else: 
            cable_flag = "warning"

        if (splice_status):
            splice_flag = "success"
        else:
            splice_flag = "warning"

        if (splice_status and cable_status):
            button_color = "success"
            next_button = "primary"
        else:
            button_color = "warning"
            next_button = "muted"
        
    return cable_text, cable_flag, splice_text, splice_flag, "all", button_color, next_button 

@app.callback(
    Output("fcp-badge", "children"),
    Output("fcp-badge", "color"),
    Output("range-button", "color"),
    # Output("fcp-button", "color"),
    Input("fcp-button", "n_clicks")
)
def on_button_click(n):
    if n is None:
        return "Not clicked.", "secondary", "secondary" #, "primary" 
    else:
        return f"Clicked {n} times.", "success", "primary" #,"success"

@app.callback(
    Output("range-badge", "children"),
    Output("range-badge", "color"),
    # Output("range-button", "color"),
    Input("range-button", "n_clicks")
)
def on_button_click(n):
    if n is None:
        return "Not clicked.", "secondary" #,"primary"
    else:
        return f"Clicked {n} times.", "success" #,"success"


# TODO: Filter Barchart Graph Object to highlight current node, displaying the LIVE and SPARE count for that node.

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
