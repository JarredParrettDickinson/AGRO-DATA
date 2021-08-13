import os
import pathlib
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf
import config 
import numpy as np
import urllib
from urllib.request import urlopen
import json
from functions import *
from database import *
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
from geojson import Feature, Point, FeatureCollection, Polygon
import pyodbc
from sqlalchemy import create_engine
# Update connection string information
server = "agrodatadb.database.windows.net"
database = "agrodatadb"
username = ""
password = ""

params = urllib.parse.quote_plus \
(r' Driver={ODBC Driver 17 for SQL Server};Server=tcp:agrodatadb.database.windows.net,1433;Database=agrodata;Uid=JarredParrett;Pwd=8!DEzXjlfPKXYTff;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
engine_azure = create_engine(conn_str,echo=True)


#Load Farm Data
df_cur = get_sub_df(None,"ALPACAS - INVENTORY", None, "United States")
df_years = pd.read_csv("~/Downloads/years.csv")
df_cat = pd.read_csv("~/Downloads/SHORT_DESC.csv")
df_dom= pd.read_csv("~/Downloads/DOMAINCAT_DESC.csv")
df_states = pd.read_csv("~/Downloads/states.csv")

#set initial variables
config.YEARS = sorted(df_cur.YEAR.unique())
config.CATEGORIES = sorted(df_cat.SHORT_DESC.unique())
config.STATES = (df_states.STATE_ALPHA.unique())
config.STATES = np.append(config.STATES, "United States")
config.DOMAINCAT_DESC = (df_dom.DOMAINCAT_DESC.unique())

# Initialize app
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = 'Agro Data'
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_lat_lon = pd.read_csv(
    os.path.join(APP_PATH, os.path.join("data", "lat_lon_counties.csv"))
)
df_lat_lon["FIPS "] = df_lat_lon["FIPS "].apply(lambda x: str(x).zfill(5))

BINS = sorted(make_bins_for_cat(df_cur).val_bins.unique())
DEFAULT_COLORSCALE = [
    "#f2fffb",
    "#bbffeb",
    "#98ffe0",
    "#79ffd6",
    "#6df0c8",
    "#69e7c0",
    "#59dab2",
    "#45d0a5",
    "#31c194",
    "#2bb489",
    "#25a27b",
    "#1e906d",
    "#188463",
    "#157658",
    "#11684d",
    "#10523e",
]

DEFAULT_OPACITY = 0.8
mapbox_access_token = "pk.eyJ1IjoiamFycmVkcGFycmV0dCIsImEiOiJja2FpaXhwZ3AwMWZwMnlvNXFyMjVoZm1kIn0.WaQOZKO-66vzeHkoAbA2vA"
mapbox_style = "mapbox://styles/mapbox/light-v9"

# App layout
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src=app.get_asset_url("logo-transparent-green.png")),
                html.H4(children="USDA Census and Survey Animal Products"),
                html.P(
                    id="description",
                    children="NASS conducts hundreds of surveys each year on issues including agricultural production, economics, demographics and the environment. Every five years NASS also conducts the Census of Agriculture, providing the only source of uniform, comprehensive agricultural data for every county in the nation. More information may be found at: www.nass.usda.gov. On development, this project is still in development; if you have thoughts or feedback, please email jarred@agrodata.app",
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="selector-cat-container",
                            children=[
                                html.P(
                                    id="selector-cat-text",
                                    children="Select Description of Variable:",
                                ),
                                 dcc.Dropdown(
                                    id="cat-dropdown",
                                    value=config.CATEGORIES[0],
                                    clearable=False,
                                    options=[
                                        {
                                            "label": str(cat),
                                            "value": str(cat),
                                        }
                                        for cat in config.CATEGORIES
                                ],
                                )
                            ],
                        ),html.Div(
                            id="selector-state-container",
                            children=[
                                html.P(
                                    id="selector-state-text",
                                    children="Select State:",
                                ),
                                 dcc.Dropdown(
                                     
                                    id="state-dropdown",
                                    value="United States",
                                    clearable=False,
                                    options=[
                                        {
                                            "label": str(state),
                                            "value": str(state),
                                        }
                                        for state in config.STATES
                                ]
                                )
                            ],
                        ),html.Div(
                            id="selector-unit-container",
                            children=[
                                html.P(
                                    id="selector-unit-text",
                                    children="Select Unit:"                                ),
                                 dcc.Dropdown(
                                    id="unit-dropdown",
                                    clearable=False,
                                    options=[
                                        {
                                            "label": str(dom),
                                            "value": str(dom),
                                        }
                                        for dom in config.DOMAINCAT_DESC
                                    ]
                                )
                            ],
                        ),
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Select a Year:",
                                ),
                                dcc.Dropdown(
                                    id="years-slider",
                                    value=min(config.YEARS),
                                    clearable=False,
                                    options=[
                                        {
                                            "label": str(year),
                                            "value": str(year),
                                        }
                                        for year in config.YEARS
                                    ]
                                ),

                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "{1}: {0}".format(
                                        min(config.YEARS), config.CATEGORIES[0]
                                    ),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=dict(
                                        data=[
                                            dict(
                                                lat=df_lat_lon["Latitude "],
                                                lon=df_lat_lon["Longitude"],
                                                text=df_lat_lon["Hover"],
                                                type="scattermapbox",
                                            )
                                        ],
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=38.72490, lon=-95.61446
                                                ),
                                                pitch=0,
                                                zoom=2.80,
                                                resetViews = True
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart - (at the moment only one chart)"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Selected Data",
                                    "value": "Selected Data",
                                }
                            ],
                            value="Selected Data",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            id="footer",
        )
    ],
)


#map components
@app.callback(
    Output("county-choropleth", "figure"),
    [Input("unit-dropdown", "value"),Input('cat-dropdown', 'value'),Input("years-slider", "value"),Input("state-dropdown", "value")],
    [State("county-choropleth", "figure")],
)
def display_map(unit, cat, year, state, figure):
    #year, cat, state, unit, figure
    string = "year: " + str(year) + " cat: " + str(cat) +  " state: " + str(state) + " unit: " + str(unit)
    print(string)
    df_cur = get_sub_df(unit, cat, year, state)

    df_cur = make_bins_for_cat(df_cur)
    BINS = sorted(df_cur.val_bins.unique())
    cm = dict(zip(BINS, DEFAULT_COLORSCALE))
    data = [
        dict(
            lat=df_lat_lon["Latitude "],
            lon=df_lat_lon["Longitude"],
            text=df_lat_lon["Hover"],
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0),
        )
    ]
    annotations = [
        dict(
            showarrow=False,
            align="right",
            text="<b>Categories Low-High</b>",
            font=dict(color="#1e392a"),
            bgcolor="#f5f5f5",
            x=0.95,
            y=0.95,
        )
    ]
    for i, bin in enumerate(reversed(BINS)):
        color = cm[bin]
        annotations.append(
            dict(
                arrowcolor=color,
                text=bin,
                x=0.95,
                y=0.85 - (i / 20),
                ax=-60,
                ay=0,
                arrowwidth=5,
                arrowhead=0,
                bgcolor="#f5f5f5",
                font=dict(color="#1e392a"),
            )
        )
    #change this to state and united states
    if str(state) != "United States":
        lat, lon = get_center_lat_long(state)
        zoom = 3.5
    else:
        lat = 38.72490
        lon = -95.61446
        zoom = 3 

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            style=mapbox_style,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso",
        
    )
        
    
    #it is reading the content here - tf we need to create maps with colors here 
    #https://github.com/jackparmer/mapbox-counties/tree/master/2015
    #base_url = "https://raw.githubusercontent.com/jackparmer/mapbox-counties/master/"
    for bin in BINS:
        geo_df = (df_cur[(df_cur['val_bins'] == str(bin))]).copy() # geo
        geo_json=make_geo_json(geo_df)
        geo_layer = dict(
            sourcetype="geojson",
            source=geo_json,
            type="fill",
            color=cm[bin],
            opacity=DEFAULT_OPACITY,
            # CHANGE THIS
            fill=dict(outlinecolor="#afafaf"),
        )
        layout["mapbox"]["layers"].append(geo_layer)

    fig = dict(data=data, layout=layout)
    return fig



@app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value"),Input("cat-dropdown", "value"),Input("state-dropdown", "value")])
def update_map_title(year, cat, state):
    out_string = str(year)+", " + str(state.upper())+",    " + str(cat)
    return out_string



@app.callback(
    Output("selected-data", "figure"),
    [
        Input("county-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
        Input('cat-dropdown', 'value'),
        Input("state-dropdown", "value"), 
        Input("unit-dropdown", "value")
    ],
)
def display_selected_data(selectedData, chart_dropdown, year, cat, state, unit):
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Click-drag on the map to select counties",
                paper_bgcolor="#f5f5f5",
                plot_bgcolor="#f5f5f5",
                font=dict(color="#828081"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )
    pts = selectedData["points"]
    fips = [str(pt["text"].split("<br>")[-1]) for pt in pts]
    for i in range(len(fips)):
        if len(fips[i]) == 4:
            fips[i] = "0" + fips[i]
    dff = get_sub_df(unit, cat, year, state)
    #print(dff.columns)
    dff = (dff[dff["COUNTY_FIP"].isin(fips)]).copy()
    if state != "United States":
        dff = dff.loc[(dff["STATE_ALPHA"] == str(state))]
    
    dff = dff.sort_values("YEAR")
    #regex_pat = re.compile(r"Unreliable", flags=re.IGNORECASE)
    #dff["Age Adjusted Rate"] = dff["Age Adjusted Rate"].replace(regex_pat, 0)

    #gets data
    #get dataframe

    title = str(year)+", " + str(state.upper())+"<br>"+ str(cat)
    dff= get_sub_df(unit, cat, year, "United States").copy()
    dff = add_state_county_string(dff)
    AGGREGATE_BY = "VALUE"
    
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    deaths_or_rate_by_fips = dff.groupby("STATE_COUNTY")[AGGREGATE_BY].sum()
    deaths_or_rate_by_fips = deaths_or_rate_by_fips.sort_values()
    # Only look at non-zero rows:
    deaths_or_rate_by_fips = deaths_or_rate_by_fips[deaths_or_rate_by_fips > 0]
    fig = deaths_or_rate_by_fips.iplot(
        kind="bar", y=AGGREGATE_BY, title=title, asFigure=True
    )

    fig_layout = fig["layout"]
    fig_data = fig["data"]

    fig_data[0]["text"] = deaths_or_rate_by_fips.values.tolist()
    fig_data[0]["marker"]["color"] = "#c9d2d3"
    fig_data[0]["marker"]["opacity"] = 1
    fig_data[0]["marker"]["line"]["width"] = 0
    fig_data[0]["textposition"] = "outside"
    fig_layout["paper_bgcolor"] = "#f5f5f5"#"#1f2630"
    fig_layout["plot_bgcolor"] = "#f5f5f5"#"#1f2630"
    fig_layout["font"]["color"] = "#1e392a"
    fig_layout["title"]["font"]["color"] = "#1e392a"
    fig_layout["xaxis"]["tickfont"]["color"] = "#1e392a"
    fig_layout["yaxis"]["tickfont"]["color"] = "#1e392a"
    fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["margin"]["t"] = 75
    fig_layout["margin"]["r"] = 50
    fig_layout["margin"]["b"] = 100
    fig_layout["margin"]["l"] = 50

    return fig

#Unit dropdown updater
@app.callback(Output('unit-dropdown', 'options'),
              [Input("cat-dropdown", "value"),Input("state-dropdown", "value")])
def return_dom_list(cat,state):
    df_cur = get_sub_df(None, cat, None, state)
    config.DOMAINCAT_DESC=df_cur.DOMAINCAT_DESC.unique()
    options=[
            {
                "label": str(dom),
                "value": str(dom),
            }
            for dom in config.DOMAINCAT_DESC
    ]
    return options

#Unit dropdown updater
@app.callback(Output('unit-dropdown', 'value'),
              [Input("cat-dropdown", "value"),Input("state-dropdown", "value")])
def return_dom_value(cat,state):
    df_cur = None
    df_cur = get_sub_df(None, cat, None, state)
    config.DOMAINCAT_DESC=df_cur.DOMAINCAT_DESC.unique()
    return config.DOMAINCAT_DESC[0]

#State dropdown updater
@app.callback(Output('state-dropdown', 'options'),
              [Input("cat-dropdown", "value")])
def return_state_list(cat):
    df_cur = get_sub_df(None, cat, None, None)
    states = sorted(df_cur.STATE_ALPHA.unique())
    states = np.append (states, "United States")
    config.STATES = (states)
    options=[
            {
                "label": str(state),
                "value": str(state),
            }
            for state in config.STATES
    ]
    return options

#Set Value to United States
@app.callback(Output('state-dropdown', 'value'),
              [Input("cat-dropdown", "value")])
def return_default_state(cat):
    return "United States"



#Year slider updater

@app.callback(Output('years-slider', 'value'),
              [Input('cat-dropdown', 'value'), Input('years-slider', 'options')])
def return_year_slider_min(cat, opts):
    if len(config.YEARS) == 0:
        return 0
    y = min(config.YEARS)
    return y


@app.callback(Output('years-slider', 'options'),
              [Input('cat-dropdown', 'value'),Input("state-dropdown", "value"), Input("unit-dropdown", "value")])
def return_year_slider(cat, state, unit):
    df_cur = get_sub_df(unit, cat, None, state)
    config.YEARS=sorted(df_cur.YEAR.unique())
    options=[
            {
                "label": str(year),
                "value": str(year),
            }
            for year in config.YEARS
    ]
    return options
    


if __name__ == "__main__":
    if False == True:
        app.run_server(debug=False, host='0.0.0.0', port='8080')#changed this to run aws
    else:
        app.run_server(debug=True, port='8080')
