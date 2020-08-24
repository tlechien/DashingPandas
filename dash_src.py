import dash
import dash_core_components as dcc
import dash_html_components as d_html
import numpy as np
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import time
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
import datetime


# !/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Server functions
def load_csv(path):
    """
        Load csv file from path using pandas
    :param path: path of the csv file
    :return: data: pandas dataframe
    """
    try:
        data = pd.read_csv(path, parse_dates=["date"])
        if data.empty:
            raise Exception("Empty: Empty file.")
    except Exception as e:
        print(f"Invalid csv path. {e}")
        exit(1)
    else:
        return data


epoch = datetime.datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


def get_marks(start, end):
    """
        Get the slider marks per month.
    :param start: start-time.
    :type start: datetime64
    :param end: end-time
    :type end: datetime64
    :return: slider marks dictionary
    :rtype: dict
    """
    result = []
    current = start
    while current <= end:
        result.append(current)
        current += relativedelta(months=1)
    return {int(unix_time_millis(m)): {'label': (str(m.strftime('%Y-%m'))),
                                       'style': {'transform': 'rotate(-90deg) translateY(-305%)',
                                                 'transform-origin': 'right top', 'text-align': 'left'}, } for m in
            result}


def get_time_frame(dataframe, start, end):
    """
        Isolate a time frame in a dataframe.
    :param dataframe: dataframe
    :param start: start-time in epoch
    :param end: end-time in epoch
    :return: dataframe slice
    """
    dates = pd.to_datetime(dataframe["date"])
    mask = (dates >= time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start / 1000.0))) & \
           (dates <= time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end / 1000.0)))
    return dataframe[mask]


# ------------------------------------------------------------------------------
# Web Core

# Pandas data acquisition

dataframe = load_csv("D:\\Users\\Utilisateur\\Desktop\\Python\\DashingPandas\\shootings.csv")
# dataframe = dataframe.groupby(['state', 'date', 'manner_of_death', 'armed', 'gender', 'race', 'city',
#                                'signs_of_mental_illness', 'threat_level', 'flee', 'body_camera', 'arms_category'])[
#     ['age']].mean()
dataframe = dataframe.groupby(['state', 'date', 'manner_of_death', 'armed', 'gender', 'race', 'city',
                               'signs_of_mental_illness', 'threat_level', 'flee', 'body_camera', 'arms_category'])[
    ['age']].mean()
dataframe.reset_index(inplace=True)
# d_dates = dataframe["date"].dt.year.unique()
d_dates = pd.to_datetime(dataframe["date"])

# ---------DEBUG------------
# print(d_dates)
# dataframe.info()
# --------------------------

# Dash initialization

app = dash.Dash("Data Analysis", external_stylesheets=[dbc.themes.DARKLY])
app.title = "Police Shootings in USA : Data analysis."

app.layout = d_html.Div(

    d_html.Div([
        d_html.Div([
            d_html.Div([], className="col-md-3"),
            d_html.Div([
                d_html.H1(children='Police Shootings in USA : Data analysis', style={'textAlign': 'center'}),
            ], className="col-md-6"),
        ], className="row m-0"),
        d_html.Div([
            d_html.Div([], className="col-md-12"),
        ], className="row m-0"),
        d_html.Div([
            d_html.Div([], className="col-md-4"),
            d_html.Div([
                d_html.H4(children='Powered by dash and pandas', style={'textAlign': 'center'}),
            ], className="col-md-4"),
        ], className="row m-0"),
        d_html.Div([
            # d_html.Div([], className="col-md-1"),
            d_html.Div([
                d_html.H5(children='Options')
            ], className="col-md-1"),
            d_html.Div([], className="col-md-11"),
            d_html.Div([
                dcc.Dropdown(
                    id="dropdown_world_map",
                    options=[{'label': dataframe.columns[x], 'value': dataframe.columns[x]} for x in
                             [2, 3, 4, 5, 7, 8, 9, 10, 11, 12]],
                    value="race",
                    style={"color": "#111111"}
                )
            ], className="col-md-3"),
            d_html.Div([
                dcc.Dropdown(
                    id="sub_dropdown_world_map",
                    value="total",
                    style={"color": "#111111"}
                )
            ], className="col-md-3"),
        ], className="row m-0"),
        d_html.Div([
            d_html.Br(),
            dcc.Graph(id="world_map", figure={}),
        ]),
        d_html.Div([
            d_html.Br(),
            dcc.RangeSlider(
                id='slider_world_map',
                updatemode='mouseup',
                step=None,
                min=unix_time_millis(d_dates.min()),
                max=unix_time_millis(d_dates.max()),
                value=[unix_time_millis(d_dates.min()),
                       unix_time_millis(d_dates.max())],
                marks=get_marks(d_dates.min(), d_dates.max()),
            ),
        ]),
        d_html.Div([
            # dcc.Graph(id="world_map", figure={}),
        ]),
    ])
)


# ------------------------------------------------------------------------------
# Sockets

@app.callback(
    [dash.dependencies.Output(component_id='world_map', component_property='figure'),
     dash.dependencies.Output(component_id="sub_dropdown_world_map", component_property='options')],
    [dash.dependencies.Input(component_id="slider_world_map", component_property='value'),
     dash.dependencies.Input(component_id="dropdown_world_map", component_property='value'),
     dash.dependencies.Input(component_id="sub_dropdown_world_map", component_property='value')])
def update_map(date_option, selector, sub_selector):
    """
        Socket function to update the world_map accordingly to sliders positions.
    :param sub_selector: dropdown option for sub-selector
    :param selector: dropdown option for main-selector
    :param date_option: slider range
    :return: fig: map figure
    """
    # ---------DEBUG------------
    x = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(date_option[0] / 1000.0))
    y = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(date_option[1] / 1000.0))
    print("date :",date_option[0], "~", x, "|", date_option[1], "~", y)
    print(f"date_option type: {type(date_option)} | selector type: {type(selector)}")
    print("selector:",selector)
    # --------------------------

    # Dataframe copy and range selection from slider
    d_dataframe = dataframe.copy()
    d_dataframe = get_time_frame(d_dataframe, date_option[0], date_option[1])

    # Dataframe data selection from dropdown
    c_name = selector
    sub_options = None
    subselector = False
    if selector != "age":
        sub_options = [{'label': x, 'value': x} for x in d_dataframe[selector].unique()]
        if sub_selector != 'total':
            c_name = sub_selector
            d_dataframe = d_dataframe[d_dataframe[selector] == sub_selector]
        else:
            c_name = 'total'
        subselector = True
        d_dataframe = d_dataframe.groupby(['state', selector])[selector].count().reset_index(name=c_name)

    # elif selector == "race":
    #     subselector = True
    #     c_name = 'total'
    #     # d_dataframe = d_dataframe.groupby(['state','race']).size().reset_index(name=c_name)
    #     # d_dataframe = d_dataframe[d_dataframe['race'] == 'Native']
    #     d_dataframe = d_dataframe.groupby(['state', 'race'])['race'].count().reset_index(name=c_name)
    #     c_name = 'race'

    # d_dataframe = d_dataframe[d_dataframe["armed"] == "knife"]
    # d_dataframe = d_dataframe.groupby(['state'])[['age']].mean()
    # dataframe.reset_index(inplace=True)
    # ---------DEBUG------------
    # print(dataframe.head())
    # print("------------------")
    print(d_dataframe.head())
    # --------------------------


    # Map creation from dataframe
    fig = px.choropleth(
        data_frame=d_dataframe,
        locationmode='USA-states',
        locations='state',
        scope="usa",
        color=c_name,
        hover_data=['state', c_name],
        color_continuous_scale="Viridis",  # px.colors.sequential.YlOrRd
        # labels={'state':'age'},
        template='plotly_dark'
    )
    return fig, sub_options


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    pd.options.display.max_columns = None

    # Dash webserver setup
    app.run_server(host="127.0.0.1", port=8080, debug=True)
