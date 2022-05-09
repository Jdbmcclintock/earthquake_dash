import requests
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from stats import *
import pendulum

external_stylesheets = [dbc.themes.BOOTSTRAP]


def serve_layout(interval=180000):
    return html.Div([dcc.Interval(id="interval", interval = interval), html.P(id="output")],
                    style = {'width':'100%', 'height':'100vh'})

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = serve_layout

@app.callback(Output("output", "children"), [Input("interval","n_intervals")])
def dashboard(n):
    last_month = get_last_month()
    json = last_months_json(last_month)
    df = extract_json(json)
    total_tnt = round(df["TNT"].sum())

    converted_tnt, unit = convert_tnt(total_tnt)
    latest_quake_location, latest_quake_magnitude = get_obspy_text(df.iloc[0, 0])
    largest_quake_location, largest_quake_magnitude = get_obspy_text(df.query("magnitude == magnitude.max()").iloc[0, 0])
    since_seventyseven = requests.get(
        "http://wfs.geonet.org.nz/geonet/ows?service=WFS&version=1.0.0&request=GetFeature&type" +
        "Name=geonet:quake_search_v1&outputFormat=json&cql_filter=origintime>=2022-05-08T18:00:00").json()
    total_quakes = len(since_seventyseven['features']) + 77000

    return dbc.Container(
        [   dbc.Row(

            dbc.Col(
                html.H1("NGMC Earthquake Dashboard", style={"fontSize":50, "textAlign":"center"}),
                width = 12, style = {"width": "100%", "height":"100%"}
            ),
        style={"height": "10%"}
        ),

            dbc.Row(
            [
            dbc.Col([
                dbc.Row(
                    dbc.Col([
                        html.P("Total earthquakes located by the NGMC: ", style={"fontSize":40,
                                                                                 'textAlign':'center',
                                                                                 "marginBottom":20,
                                                                                 "marginTop":30}),
                        html.P(total_quakes, style={"fontSize":200,
                                               'textAlign':'center',
                                               "marginBottom":0,
                                               "marginTop":0}),
                        html.Br(style={"fontSize":30}),
                        html.P("Latest Earthquake",  style={"fontSize":20,
                                                            'textAlign':'center',
                                                            "marginBottom":0,
                                                            "marginTop":0}),

                        html.P(latest_quake_magnitude + ", " + latest_quake_location, style={"fontSize": 30,
                                                              'textAlign': 'center',
                                                              "marginBottom": 15,
                                                              "marginTop": 0
                                                              }),
                        html.P("Earthquakes located in past 30 days: ",
                               style={"fontSize": 20,
                                      'textAlign': 'center',
                                      "marginBottom": 0,
                                      "marginTop": 0
                                     }),
                        html.P(len(df),
                               style={"fontSize": 40,
                                      'textAlign': 'center',
                                      "marginBottom": 15,
                                      "marginTop": 0
                                      }),
                        html.P("Largest earthquake in past 30 days:",
                               style={"fontSize": 20,
                                      'textAlign': 'center',
                                      "marginBottom": 0,
                                      "marginTop": 0
                                      }
                               ),
                        html.P(largest_quake_magnitude + ", " + largest_quake_location,
                               style={"fontSize": 30,
                                      'textAlign': 'center',
                                      "marginBottom": 15,
                                      "marginTop": 0
                                      }),
                        html.P("Total energy released by EQs located by NGMC last 30 days: ",
                               style={"fontSize": 20,
                                      'textAlign': 'center',
                                      "marginBottom": 0,
                                      "marginTop": 0
                                      }),
                        html.P(str(converted_tnt) + unit, style={"fontSize": 30, 'textAlign': 'center'}),
                        html.P("last run: " + pendulum.now('Pacific/Auckland').to_datetime_string(), style={"fontSize": 10, 'textAlign': 'left'})
    ],
                        style={"height  ":"100%"}),
                style = {"height" : "100%"}
                ),

                ]

            ),
            dbc.Col(
                dcc.Graph(figure=
                px.scatter_mapbox(df,
                        lon = df.longitude,
                        lat = df.latitude,
                        center = dict(lat = -40, lon = 173),
                        zoom = 4,
                        size = [i**3 for i in df.magnitude],
                        color= "depth",
                        range_color = [0, 300],
                        opacity = 0.5,
                        mapbox_style= 'open-street-map'), style = {"height":"100%"}), style = {"height" : "100%"}
            )
            ],
        style = {"height" : "90%"}
    )], style={"height": "100vh"}, fluid = True
    )


if __name__ == '__main__':
    app.run_server(debug = True, port= 8053)

