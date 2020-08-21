import dash
import dash_core_components as dcc
import dash_html_components as d_html
import numpy as np
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


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


# ------------------------------------------------------------------------------
# Web Core

# Pandas data acquisition

dataframe = load_csv("D:\\Users\\Utilisateur\\Desktop\\Python\\DashingPandas\\shootings.csv")
dataframe = dataframe.groupby(['state', 'date', 'manner_of_death', 'armed', 'gender', 'race', 'city',
                               'signs_of_mental_illness', 'threat_level', 'flee', 'body_camera', 'arms_category'])[
    ['age']].mean()
dataframe.reset_index(inplace=True)
d_dates = dataframe["date"].dt.year.unique()

# Dash initialization

app = dash.Dash("Data Analysis", external_stylesheets=[dbc.themes.DARKLY])
app.title = "Police Shootings in USA : Data analysis."

app.layout = d_html.Div(

    d_html.Div([
        d_html.Div([
            d_html.Div([], className="col-md-3"),
            d_html.Div([
                d_html.H1(children='Police Shootings in USA : Data analysis'),
            ], className="col-md-6"),
        ], className="row m-0"),
        d_html.Div([
            d_html.Div([], className="col-md-12"),
        ], className="row m-0"),
        d_html.Div([
            d_html.Div([], className="col-md-4"),
            d_html.Div([
                d_html.H3(children='Powered by dash and pandas'),
            ], className="col-md-4"),
        ], className="row m-0"),
        d_html.Div([
            d_html.Br(),
            dcc.Graph(id="world_map", figure={}),
            d_html.Br(),
            dcc.RangeSlider(
                id="slider_world_map",
                marks={int(i): str(i) for i in list(d_dates)},
                min=min(d_dates),
                max=max(d_dates),
                value=[min(d_dates), max(d_dates)]
            )
        ])
    ])
)


# ------------------------------------------------------------------------------
# Sockets

@app.callback(
    dash.dependencies.Output(component_id='world_map', component_property='figure'),
    [dash.dependencies.Input(component_id="slider_world_map", component_property='value')])
def update_map(option):
    """
        Socket function to update the world_map accordingly to sliders positions.
    :param option: slider range
    :return: fig: map figure
    """
    # ---------DEBUG------------
    print(option)
    print(type(option))
    # --------------------------

    # Dataframe copy and range selection from slider
    d_dataframe = dataframe.copy()
    if option:
        mask = (d_dataframe['date'].dt.year >= option[0]) & (d_dataframe['date'].dt.year <= option[1])
        d_dataframe = d_dataframe[mask]
    # d_dataframe = d_dataframe[d_dataframe["armed"] == "knife"]
    # d_dataframe = d_dataframe.groupby(['state'])[['age']].mean()

    # ---------DEBUG------------
    # print(dataframe.head())
    # print("------------------")
    # print(d_dataframe.head())
    # --------------------------

    # Map creation from dataframe
    fig = px.choropleth(
        data_frame=d_dataframe,
        locationmode='USA-states',
        locations='state',
        scope="usa",
        color='age',
        hover_data=['state', 'age'],
        color_continuous_scale="Viridis",  # px.colors.sequential.YlOrRd
        # labels={'state':'age'},
        template='plotly_dark'
    )
    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    pd.options.display.max_columns = None

    # Dash webserver setup
    app.run_server(host="127.0.0.1", port=8080, debug=True)
