# Base Import
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import os
import redis
from redis_tasks import start_celery
import json
import pandas as pd
import colorama
from datetime import datetime as dt
import datetime
# Custom Imports
from async_pull import country_total_c_r_d
from graphs.world_map import request_world_map
from graphs.world_map_mapbox import request_candlestick


PLOTLY_LOGO = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fbigredmarkets.com%2Fwp-content%2Fuploads%2F2020%2F03%2FCovid-19.png&f=1&nofb=1"

BS = "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"

external_scripts = [{
        'type': 'text/javascript',
        'src': "https://cdn.flourish.rocks/flourish-live-v4.4.1.min.js",
    }]

app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG], external_scripts=external_scripts)

server = app.server
app.title = 'Covid-19 Map'

"""-----------------------------Connect Redis & Setup Application Data Management----------------------------------"""
port = int(os.environ.get('PORT', 6379))
listen = ['TO_Date', 'USA_Today']

TIMEOUT = 60

# Run Heroku
ON_HEROKU = os.environ.get('ON_HEROKU')
os.environ.get('ON_HEROKU')

if ON_HEROKU:
    # get the heroku port
    port = int(os.environ.get('PORT', 17995))  # as per OP comments default is 17995


redis_url = os.getenv('REDIS_URL', f'redis://localhost:{port}')

conn = redis.from_url(redis_url)

redis_instance = redis.StrictRedis.from_url(redis_url)


start_celery()

"""-----------------------------------Start Redis Tasks & transcode into dataframe------------------------------"""
# Home Page Tasks

# Search Country
def get_country(country):

    jsonified_df = redis_instance.get(
        'c_date_to_today'
    ).decode("utf-8")
    df = pd.DataFrame(json.loads(jsonified_df))

    if country == 'United States':
        df2 = df['countryRegion'].str.contains('US')

        print('this is the issue focus')
        print(df[df2])
        df = df[df2]
        for x in df.head():
            print(x)

        return df[df2]
    else:
        try:
            df2 = df['countryRegion'].str.contains(country)
            return df[df2]
        except:
            return df

def get_home_map_animation(country):
    today = datetime.date.today()

    week_ago = today - datetime.timedelta(days=7)
    print(week_ago)

    days = []
    while week_ago != today:
        week_ago = week_ago + datetime.timedelta(days=1)
        days.append(week_ago)

    print(f'days = {days}')

    finished_redis_fetch = []
    for day in days:
        print(f'searching redis on: {day}-dataframe')
        jsonified_df = redis_instance.get(
            f'{day}-dataframe'
        ).decode("utf-8")

        df = pd.DataFrame(json.loads(jsonified_df))
        if country == 'United States':
            country = 'US'
            df2 = df['countryRegion'].str.contains(country)
            print('fuckhead')
            print(df[df2])
            finished_redis_fetch.append(df[df2])
        else:
            df2 = df['countryRegion'].str.contains(country)
            finished_redis_fetch.append(df[df2])

    print('This is the DF to Focus on')
    print(finished_redis_fetch)

    return finished_redis_fetch

def get_basic_country_geo():
    jsonified_df = redis_instance.get(
        'country-basic-geo-dataframe'
    ).decode("utf-8")
    df = pd.DataFrame(json.loads(jsonified_df))
    return df


def get_dropdown_options():
    options = []
    df = get_basic_country_geo()
    df = df.to_dict()
    for x, y in zip(df['country'], df['name']):
        options.append({'label': df['name'][y], 'value': df['name'][y]})

    return options


"""----------------------------Static Assets-----------------------------------------------------"""

PLOTLY_LOGO = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fbigredmarkets.com%2Fwp-content%2Fuploads%2F2020%2F03%2FCovid-19.png&f=1&nofb=1"


"""-------------------------------Layout---------------------------------------------------------"""
"""Navbar"""
# dropdown Items

# make a reuseable navitem for the different examples
nav_item = dbc.NavItem(dbc.NavLink("Join the Pip Install Crew",
                                   href="https://pipinstallpython.com/"))

# make a reuseable dropdown for the different examples
dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Youtube Channel",
                             href='https://www.youtube.com/channel/UC-pBvv8mzLpj0k-RIbc2Nog?view_as=subscriber'),
        dbc.DropdownMenuItem("Udemy Dash", href='https://www.udemy.com/course/plotly-dash/?referralCode=16FC11D8981E0863E557'),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Project Github", href='https://github.com/cryptopotluck/covid-country-compare'),
        dbc.DropdownMenuItem("Plotly / Dash", href='https://dash.plot.ly/'),
        dbc.DropdownMenuItem("Dash Bootstrap", href='https://dash-bootstrap-components.opensource.faculty.ai/'),
    ],
    nav=True,
    in_navbar=True,
    label="Important Links",
)

# Navbar Layout
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="40px")),
                        dbc.Col(dbc.NavbarBrand("Covid-19 Dashboard Course", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="https://plot.ly",
            ),
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav(
                    [nav_item,
                     dropdown,
                     ], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-5",
)


"""Body Components"""
# Structure Top Cards

# def total_data_card(request, header):
#     card_content = [
#         dbc.CardHeader(header),
#         dbc.CardBody(
#             [
#                 html.H5(f'{country_total_c_r_d.main(request):,}', className="card-title"),
#             ]
#         ),
#     ]
#     return card_content
"""Body"""

discord_chat_app = dbc.Card(
    dbc.CardBody(
        html.Iframe(src='https://e.widgetbot.io/channels/737637067529519168/737637071275032657', width='100%', height='800',),
    ))

tab_country_lookup = dbc.Card(
    dbc.CardBody(
        [
            # Quick Link Useful Information
            dbc.Row([
                dbc.Col(
                   dbc.FormGroup(
                    [
                        dcc.Dropdown(
                            id="country_location",
                            options=get_dropdown_options(),
                        ),
                    ]
                ), sm=5, md=5
                ),
                dbc.Col(dbc.Button("Search", color="light", id='button-search-location', className="mr-1"), sm=2, md=2),
                dbc.Col(
                        dbc.FormGroup(
                            [
                                dcc.Dropdown(
                                    id="country_location_two",
                                    options=get_dropdown_options(),
                                ),
                            ]
                        ), sm=5, md=5
                    ),
            ]),
            dbc.Row(
                [
                    # dbc.Col(
                    #     dbc.Card(total_data_card(request='confirmed', header='Confirmed Cases'), color="primary", inverse=True)),
                    # dbc.Col(
                    #     dbc.Card(total_data_card(request='recovered', header='Total Recovered'), color="success", inverse=True)),
                    # dbc.Col(dbc.Card(total_data_card(request='deaths', header='Total Deaths'), color="danger", inverse=True)),
                ]),
            dbc.Row(
                [
                    # left Country
                    dbc.Col([
                        html.Div(id='seven-day-map'),
                        html.Div(id='candle-graph')
                    ], md=6, lg=6),
                    # Right Country
                    dbc.Col([
                        html.Div(id='seven-day-map-two'),
                        html.Div(id='candle-graph-two')
                    ], md=6, lg=6)]
            ),
            dbc.Row([dbc.Col(html.Div(),  md=2, lg=2), dbc.Col(html.Div(id='search-location'),  md=8, lg=8), dbc.Col(html.Div(),  md=2, lg=2)])
        ]
    ),
    className="mt-3",
)



"""Tab Body"""
# TODO: Name change to tab_country_search
# tab_snapshot = dbc.Card(
#     dbc.CardBody(
#     [
#     dbc.Row(
#     [
#         # Header
#         dbc.Row([dbc.Col(html.Div(), width=3),
#                  dbc.Col(dcc.DatePickerSingle(
#                      id='date-picker-single',
#                      min_date_allowed=dt(2020, 3, 23),
#                      max_date_allowed=datetime.date.today() - datetime.timedelta(days=1),
#                      initial_visible_month=datetime.date.today() - datetime.timedelta(days=1),
#                      date=datetime.date.today() - datetime.timedelta(days=12)
#                  ), width=6),
#                  dbc.Col(html.Div(), width=3)
#                  ]
#                 ),
#         # Body
#         dbc.Row([
#             dbc.Col(html.Div(id='updated-world-map', style={'height': '85vh'}), style={'width': '100vw'}, lg=6, md=12),
#             dbc.Col(html.Div(id='barchart', style={'height': '85vh'}), lg=6, md=12)]),
#         dbc.Row([]),
#         dbc.Row([dbc.Col(html.Div(),  md=2, lg=2), dbc.Col(html.Div(id='date-content'),  md=8, lg=8), dbc.Col(html.Div(),  md=2, lg=2)])
#     ]
# )
#     ]))




"""Tabs"""

tabs = dbc.Tabs(
    [
        dbc.Tab(
             tab_country_lookup, label="Country Compare"
        ),
        dbc.Tab(
             discord_chat_app, label="Dash Chat App"
        )
    ]
)

"""Body"""
# rows
body = html.Div(
    [
        dbc.Toast(
            dbc.CardLink("pip install Shop", href="https://pipinstallpython.com/shop/"),
            id="positioned-toast",
            header="Learn How to Build this Dashboard & More",
            is_open=True,
            dismissable=True,
            icon="danger",
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),

        dbc.Row(html.P('')),
        dbc.Row(html.Div(tabs, style={'width': '100%'})),
    ]
)


"""Layout"""
# Renders the Layout

app.layout = html.Div(
        [navbar, body]
)

@app.callback(
    Output("seven-day-map", "children"),
    [Input("button-search-location", "n_clicks"), Input('country_location', 'value')]
)
def on_button_click2(n, v):
    if n is None:
        return 'None'
    else:
        df = get_country(v)
        print('Bookmark this location2')
        print(df)
        print(df['lat'][0])


        return dcc.Graph(figure=request_world_map(get_home_map_animation(v), lat=float(df['lat'][0]), long=float(df['long'][0])),
                                      style={'height': '75vh'})

@app.callback(
    Output("seven-day-map-two", "children"),
    [Input("button-search-location", "n_clicks"), Input('country_location_two', 'value')]
)
def on_button_click2(n, v):
    if n is None:
        return 'None'
    else:
        df = get_country(v)

        print(df)
        print(df['lat'][0])


        return dcc.Graph(figure=request_world_map(get_home_map_animation(v), lat=float(df['lat'][0]), long=float(df['long'][0])),
                                      style={'height': '75vh'})

@app.callback(
    Output("candle-graph", "children"),
    [Input("button-search-location", "n_clicks"), Input('country_location', 'value')]
)
def on_button_click3(n, v):
    # n = look for user click
    # v = country name
    if n is None:
        return 'None'
    else:
        df = get_country(v)
        print('length Check lets see how many rows it has')
        length = 0
        locations = []

        #if df only has one row render it this way
        if len(df) == 1:
            locations.append({'provinceState': df['provinceState'][0], 'countryRegion': df['countryRegion'][0]})
            print(f'some strange shit - {df}')
            print({'provinceState': df['provinceState'][0], 'countryRegion': df['countryRegion'][0]})
            return dcc.Graph(figure=request_candlestick(get_home_map_animation(v), country=locations[0]),
                             style={'height': '75vh'})
        # if df has one < row render it this way
        else:
            for x in df.head():
                print(x)
            print(f"some stranger shit - {df['countryRegion'][0]}")
            return dcc.Graph(figure=request_candlestick(get_home_map_animation(v), country=df['countryRegion'][0]),
                                          style={'height': '75vh'})

@app.callback(
    Output("candle-graph-two", "children"),
    [Input("button-search-location", "n_clicks"), Input('country_location_two', 'value')]
)
def on_button_click3(n, v):
    # n = look for user click
    # v = country name
    if n is None:
        return 'None'
    else:
        df = get_country(v)
        print('length Check lets see how many rows it has')
        length = 0
        locations = []

        #if df only has one row render it this way
        if len(df) == 1:
            locations.append({'provinceState': df['provinceState'][0], 'countryRegion': df['countryRegion'][0]})

            print({'provinceState': df['provinceState'][0], 'countryRegion': df['countryRegion'][0]})
            return dcc.Graph(figure=request_candlestick(get_home_map_animation(v), country=locations[0]),
                             style={'height': '75vh'})
        # if df has one < row render it this way
        else:
            for x in df.head():
                print(x)
            print(f"some stranger shit - {df['countryRegion'][0]}")
            return dcc.Graph(figure=request_candlestick(get_home_map_animation(v), country=df['countryRegion'][0]),
                                          style={'height': '75vh'})



if __name__ == "__main__":
    app.scripts.append_script({'external_url': 'https://e.widgetbot.io/channels/737637067529519168/737637071275032657'})
    app.run_server(debug=False, port=50620)