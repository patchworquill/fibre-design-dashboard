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
from allocation import *
from upload import *

cyto.load_extra_layouts()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], meta_tags=[
                {"name": "viewport", "content": "width=device-width"}],)

colors = {'Live': 'lightpink',
          'Spare': 'khaki',
          'Reserved': 'lightblue'}

#################################################
#
#
#                 BOOTSTRAP LAYOUT
#
#
#################################################

def make_layout():
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
                dbc.Row([html.P(str(file), id='file-list', style={"font-size": "50%"})]),
                dbc.Row([
                    html.Div(id='output-data-upload'),
                ]),
            ], width=2,
            ),

            dbc.Col([
                html.H4("COID"),
                html.H1("PROJ", id="project_name")
            ]),
            dbc.Col([
                html.H4("FSA"),
                html.H1("FSA#", id="fsa_name")
            ]),
            dbc.Col([
                html.H4("Ⓣ NODES"),
                html.H2(html.Span(
                    "Num_Nodes",
                    id="tooltip-target",
                    style={"cursor": "pointer"}, #"textDecoration": "underline"
                )),
                dbc.Tooltip(
                    "Nodes_List",
                    target="tooltip-target",
                ),
            ]),
            dbc.Col([
                html.H4("Ⓣ EDGES"),
                # html.H2(str(nx.number_of_edges(G))),
                html.H2(html.Span(
                    "Num_Edges",
                    id="tooltip-target2",
                    style={"cursor": "pointer"}, #"textDecoration": "underline"
                )),
                dbc.Tooltip(
                    "Edges",
                    target="tooltip-target2",
                ),
            ]),
            dbc.Col([
                html.H4("LIVE"),
                html.H2("0", 
                        id="live-count"
                )
            ]),
            dbc.Col([
                html.H4("SPARE"),
                html.H2("0", id="spare-count") #, "SPARE2", "SPARE3"
            ]),
            dbc.Col([
                html.H4("RSVD"),
                html.H2("0", id="reserve-count") #, "SPARE2", "SPARE3"
            ]),
            dbc.Col([
                html.H4("DEGREE"),
                html.H2(html.Span("MAX", id="tooltip-target3")),
                dbc.Tooltip(
                    "Degree",
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
                        html.P(id='empty-div', children="", style={"font-size": "80%"})
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
                        # width="100px",
                    ),
                    dbc.Col([
                        html.Div([
                            dash_table.DataTable(
                                id='memory-table-nodes',
                                # sort_action='native',
                                editable=True,
                                columns=[{'name': i, 'id': i}
                                        for i in nodes_df.columns],
                                fixed_rows={'headers': True},
                                style_table={
                                    'overflowY': 'auto',
                                    # 'height': '40vh',
                                    'width': '60vw',
                                    }
                            ),
                        ],
                        ),
                        html.Div([
                            dash_table.DataTable(
                                id='memory-table-edges',
                                # sort_action='native',
                                editable=True,
                                columns=[{'name': i, 'id': i}
                                        for i in edges_df.columns],
                                fixed_rows={'headers': True},
                                style_table={
                                    'overflowY': 'auto',
                                    'width': '60vw',
                                    }
                            ),
                        ],
                        )
                    ],
                    ),
                ],
                # className="row h-40",
                id="data-table"
                ),
            ],
            # style={"height": "60vh"}
            ),
        ],),

        ############# Stats
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
        cable_status, cable_list = cable_activities(G, edges_df)
        edges_df["CableActivity"] = cable_list
        cable_list = filter(None, cable_list)
        cable_text = str("CABLE")

        splice_status, splice_list = splice_activities(G, nodes_df, cable_list)
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
            selected_list = nodes_df.at[nodes_df.index[nodes_df['Struc'] == int(node["id"])], "Struc"].tolist()
            selected_list.append() #nodes_df.at[int(node["id"]), "NODE"])
        # selected_list.append(nodes_df.at[nodes_df.index[nodes_df['Struc'] == (int(node["id"]))], "NODE"])
        print(selected_list)

    return selected_list


@app.callback(Output('memory-table-nodes', 'data'),
              Input('node-selector-dropdown','value')  # tapNodeData
              )
def on_data_set_table(nodeList):
    filtered = nodes_df[nodes_df['Struc'].isin(list(nodeList))]

    return filtered.to_dict('records')

@app.callback(Output('memory-table-edges', 'data'),
              Input('node-selector-dropdown','value')  # tapNodeData
              )
def on_data_set_table(nodeList):
    filtered = edges_df[edges_df['End SB'].isin(list(nodeList))]

    return filtered.to_dict('records')


# TODO: Filter Barchart Graph Object to highlight current node, displaying the LIVE and SPARE count for that node.
@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)
            df = parse_contents(data, name)
            print(df)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]

def parse_contents(contents, filename):
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
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    return df

@app.callback(
    Output("project_name", "children"),
    Output("fsa_name", "children"),
    Input("file-list", "children"),
)
def update_data(files):
    fname = files[0].get('props', 0).get('children', 0).get('props', 0).get('children')
    print("This file is: ", fname)
    try:
        endo = fname.split(") ")[1]
        project, fsa = endo.split(" ")
        fsa = fsa.split(".")[0]
    except KeyError as e:
        print(e)
        return 0, 0
    return project, fsa

def load_everything(file='Data\(Fibre Data) OKRG 1031B_.xlsx'):
    nodes_df, edges_df = load_file(file)
    G = create_graph(edges_df) # create_graph assumes schema is Number | Start | End | etc1 | etc2 | etc3 ...
    T = create_tree(G)

    cy = nx.readwrite.json_graph.cytoscape_data(G)

    NODES_LIST = list(
        x for x in nodes_df['Struc'].unique() if pd.isnull(x) == False)
    nodes_cy = [{'data': {'id': x, 'label': x}} for x in list(nodes_df.Struc)]

    return nodes_df, edges_df, G, T, cy, NODES_LIST, nodes_cy

def make_figs():
    # Allocation Plot
    try:
        data=[
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
                        ]
    except KeyError as e:
        data = []
        print("Missing columns in excel / csv:")
        print(e)
    fig = go.Figure(data)
    fig.update_layout(barmode='stack', title='Fiber Allocation')

    # Capacity Plot
    try:
        data=[
            go.Bar(
                name="Capacity", x=edges_df["End"], y=edges_df["Cap"], marker_color="lightgrey"),  # marker_color=colors['Live']
        ]
    except KeyError as e:
        data = []
        print("Missing capacity information.")
        print(e)
    fig2 = go.Figure(data)
    fig2.update_layout(barmode='stack', title='Fiber Capacity')

    return fig, fig2

if __name__ == '__main__':
    df = []
    file = "K:\\Clients\\AFL - AFL\\2021\\022 - OGDN\\OGDN 1142A\\DFD\\R\\(Fibre Data) OGDN 1142A.xlsx"
    nodes_df, edges_df, G, T, cy, NODES_LIST, nodes_cy = load_everything(file)
    fig, fig2 = make_figs()
    make_layout()
    server = app.run_server(debug=True)