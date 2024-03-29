# !/usr/bin/env python
import datetime
import time
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as d_html
import numpy as np
import pandas as pd
import plotly.express as px
from dateutil.relativedelta import relativedelta


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
                                                 'transformOrigin': 'right top', 'textAlign': 'left', 'width': 'fit-content'}} for m in
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

# Pandas data acquisition

dataframe = load_csv("./shootings.csv")
dataframe = dataframe.groupby(['state', 'date', 'manner_of_death', 'armed', 'gender', 'race', 'city',
                               'signs_of_mental_illness', 'threat_level', 'flee', 'body_camera', 'arms_category'])[
    ['age']].mean()
dataframe.reset_index(inplace=True)
d_dates = pd.to_datetime(dataframe["date"])

# ------------------------------------------------------------------------------
# Web Core

# Dash initialization

app = dash.Dash("Data Analysis", external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
app.title = "Police Shootings in USA : Data analysis."

# Elements content

world_map_dd = dict(
    options=[{'label': dataframe.columns[x], 'value': dataframe.columns[x]} for x in
             [2, 3, 4, 5, 7, 8, 9, 10, 11, 12]],
    value="race",
    clearable=False,
    style={"color": "#111111"}
)
world_map_sdd = dict(
    value="Total",
    clearable=False,
    style={"color": "#111111"}
)
world_map_ri = dict(
    options=[
        {'label': "  cardinal", 'value': "cardinal"},
        {'label': "  ratio", 'value': "ratio"}
    ],
    value="cardinal",
    labelStyle={'marginRight': '5px', 'textAlign': 'center', 'marginLeft': '2px'},
    style={"color": "#F9F9F9", 'display': 'flex', 'position': 'relative', 'top': '15%'}
)
map_style = dict(
    options=[{'label': x['y'][0], 'value': x['y'][0]} for x in px.colors.sequential.swatches().data],
    value="Viridis",
    clearable=False,
    style={"color": "#111111"}
)
world_map_rs = dict(
    id='slider_world_map',
    updatemode='mouseup',
    step=None,
    min=unix_time_millis(d_dates.min()),
    max=unix_time_millis(d_dates.max()),
    value=[unix_time_millis(d_dates.min()),
           unix_time_millis(d_dates.max())],
    marks=get_marks(d_dates.min(), d_dates.max()),
)
div_menu_l1 = dict(children=[
    d_html.Div([d_html.H5(children='Options')], className="col-md-1"),
    d_html.Div([], className="col-md-9"),
    d_html.Div([dcc.Dropdown(id={'type': 'dynamic-dd', 'index': 2}, **world_map_dd)], className="col-md-1",
               style={'display': 'none'}),
    d_html.Div([dcc.Dropdown(id={'type': 'dynamic-sdd', 'index': 2}, **world_map_sdd)], className="col-md-1",
               style={'display': 'none'}),
    d_html.Div([dcc.Dropdown(id={'type': 'dynamic-dd', 'index': 1}, **world_map_dd)], className="col-md-3"),
    d_html.Div([dcc.Dropdown(id={'type': 'dynamic-sdd', 'index': 1}, **world_map_sdd)], className="col-md-3"),
    d_html.Div([dcc.RadioItems(id="radio_world_map", **world_map_ri)], className="col-md-2",
               style={'display': 'hidden'}),
    d_html.Div([d_html.Button("Enable comparison", id="comparison",
                              style={'display': 'flex', 'position': 'relative', 'top': '15%', 'float': 'right'})],
               className="col-md-2"),
    d_html.Div([dcc.Dropdown(id="map_style", **map_style)], className="col-md-2")
])
div_menu_l2 = dict(children=[
    d_html.Div([d_html.H5(children='Options')], className="col-md-1"),
    d_html.Div([], className="col-md-7"),
    d_html.Div([d_html.Button("Disable comparison", id="comparison",
                              style={'display': 'flex', 'position': 'relative', 'top': '15%', 'float': 'right'})],
               className="col-md-2"),
    d_html.Div([dcc.Dropdown(id="map_style", **map_style)], className="col-md-2"),
    d_html.Div([d_html.Br()], className="col-md-12"),
    d_html.Div([dcc.Dropdown(id={'type': 'dynamic-dd', 'index': 1}, **world_map_dd)], className="col-md-2"),
    d_html.Div([dcc.Dropdown(id={'type': 'dynamic-sdd', 'index': 1}, **world_map_sdd)], className="col-md-2"),
    d_html.Div([], className="col-md-1"),
    d_html.Div([dcc.RadioItems(id="radio_world_map", **world_map_ri)], className="col-md-2",
               style={'display': 'hidden'}),
    d_html.Div([], className="col-md-1"),
    d_html.Div([dcc.Dropdown(id={'type': 'dynamic-dd', 'index': 2}, **world_map_dd)], className="col-md-2"),
    d_html.Div([dcc.Dropdown(id={'type': 'dynamic-sdd', 'index': 2}, **world_map_sdd)], className="col-md-2")
])
div_map_l1 = dict(children=[
    d_html.Br(),
    dcc.Graph(id={
        'type': 'dynamic-map',
        'index': 1
    }, style={"height": "70vh", "width": "100%"}),
    dcc.Graph(id={
        'type': 'dynamic-map',
        'index': 2
    }, style={'display': 'none'})
])
div_map_l2 = dict(children=[
    d_html.Br(),
    d_html.Div([
        d_html.Div([dcc.Graph(id={
            'type': 'dynamic-map',
            'index': 1
        }, style={"height": "70vh"})], id="map_1", className="col-md-6"),
        d_html.Div([dcc.Graph(id={
            'type': 'dynamic-map',
            'index': 2
        }, style={"height": "70vh"})], id="map_2", className="col-md-6")
    ], className="row m-0")
])

# Html layout

app.layout = d_html.Div(
    d_html.Div([
        dcc.Store(id="menu_state"),
        dcc.Store(id="map_update"),
        d_html.Div(id="output-clientside"),
        d_html.Div([
            d_html.Div([], className="col-md-2"),
            d_html.Div([
                d_html.H1(children='Police Shootings in USA : Data analysis',
                          style={'textAlign': 'center', 'font-size': '3.5vw'}),
            ], className="col-md-8"),
        ], className="row m-0"),
        d_html.Div([d_html.Div([], className="col-md-12")], className="row m-0"),
        d_html.Div([
            d_html.Div([], className="col-md-4"),
            d_html.Div([
                d_html.H4(children='Powered by dash and pandas', style={'textAlign': 'center'}),
            ], className="col-md-4"),
        ], className="row m-0"),
        d_html.Div([
            d_html.Div(**div_menu_l2, id="div_menus", className="row m-0"),
            d_html.Div(**div_map_l1, id='div_map'),
            d_html.Div([
                d_html.Div([d_html.Br(), dcc.RangeSlider(**world_map_rs), d_html.Br(), d_html.Br()], className="col-md-12"),
            ], id="div_timeline", className="row m-0"),
        ], id="Layout1"),
    ])
)


# ------------------------------------------------------------------------------
# Sockets

def update_map(date_option, selector, sub_selector, radio, map_style):
    """
        Socket function to update the world_map accordingly to sliders positions.
    :param map_style: style of the map
    :param radio: selector cardinal/ratio
    :param sub_selector: dropdown option for sub-selector
    :param selector: dropdown option for main-selector
    :param date_option: slider range
    :return: fig: map figure
    :return: sub_options: sub-selector options
    :return show: style for sub-selector
    :return show2: style for radioitem
    """

    # Dataframe copy and range selection from slider
    d_dataframe = dataframe.copy()
    if selector == 'signs_of_mental_illness':
        d_dataframe['signs_of_mental_illness'] = d_dataframe['signs_of_mental_illness'].astype(str)
    elif selector == 'body_camera':
        d_dataframe['body_camera'] = d_dataframe['body_camera'].astype(str)
    d_dataframe = get_time_frame(d_dataframe, date_option[0], date_option[1])

    # Dataframe data selection from dropdowns
    c_name = selector
    sub_options = []
    subs = ['age']
    if selector != "age":
        subs = list(d_dataframe[selector].unique())
        subs.append('Total')
        sub_options = [{'label': str(x), 'value': x if type(x) != np.bool_ else str(x)} for x in subs]
        if sub_selector != 'Total' and list(filter(lambda x: x['label'] == sub_selector, sub_options)):
            c_name = sub_selector
        else:
            c_name = 'Total'
        d_dataframe = d_dataframe.groupby(['state', selector])[selector].count().reset_index(name='count')
        d_dataframe = d_dataframe.groupby(['state', selector])['count'].aggregate('first').unstack().reset_index()
        d_dataframe['Total'] = d_dataframe.sum(axis=1)
        if radio == "ratio" and c_name != "Total":
            for x in subs[:-1]:
                d_dataframe[f"{x}%"] = d_dataframe[x] / d_dataframe["Total"] * 100
            c_name = sub_selector + "%"
            subs = [f"{sub}%" for sub in subs[:-1]]
    d_dataframe.fillna(0, inplace=True)

    # Map creation from dataframe
    # color = np.log10(d_dataframe[c_name]) for log color scale
    fig = px.choropleth(
        data_frame=d_dataframe,
        locationmode='USA-states',
        locations='state',
        scope="usa",
        color=c_name,
        range_color=(d_dataframe.min()[c_name], d_dataframe.max()[c_name]),
        hover_name='state',
        hover_data={sub: ":.1f" for sub in subs},
        color_continuous_scale=map_style,
        template='plotly_dark',
    )
    show = {'display': 'none'} if not sub_options else {"color": "#111111"}
    show2 = {'display': 'none'} if not sub_options or c_name == "Total" else {'display': 'flex', 'position': 'relative',
                                                                              'top': '15%'}
    return fig, sub_options, show, show2


@app.callback(
    [dash.dependencies.Output(component_id='div_menus', component_property='children'),
     dash.dependencies.Output(component_id='div_map', component_property='children'),
     dash.dependencies.Output(component_id="menu_state", component_property='data')],
    [dash.dependencies.Input(component_id="comparison", component_property='n_clicks')],
    [dash.dependencies.State(component_id="menu_state", component_property='data')]
)
def enable_comparison(click, state):
    """
        Update layout to allow/disallow comparison when button is pressed.
    :param click: button click
    :param state: stored value of the map_layout
    :return: new layouts and state value
    """
    if state:
        return div_menu_l2["children"], div_map_l2["children"], 0
    else:
        return div_menu_l1["children"], div_map_l1["children"], 1


@app.callback(
    [dash.dependencies.Output(component_id={'type': 'dynamic-map', 'index': 1}, component_property='figure'),
     dash.dependencies.Output(component_id={'type': 'dynamic-sdd', 'index': 1}, component_property='options'),
     dash.dependencies.Output(component_id={'type': 'dynamic-sdd', 'index': 1}, component_property='style'),
     dash.dependencies.Output(component_id="radio_world_map", component_property='style'),
     dash.dependencies.Output(component_id="map_update", component_property='data')],
    [dash.dependencies.Input(component_id="slider_world_map", component_property='value'),
     dash.dependencies.Input(component_id={'type': 'dynamic-dd', 'index': 1}, component_property='value'),
     dash.dependencies.Input(component_id={'type': 'dynamic-sdd', 'index': 1}, component_property='value'),
     dash.dependencies.Input(component_id="radio_world_map", component_property='value'),
     dash.dependencies.Input(component_id="map_style", component_property='value'),
     dash.dependencies.Input(component_id="menu_state", component_property='data')]
)
def update_map1(date_option, selector, sub_selector, radio, map_style, m_state):
    return list(update_map(date_option, selector, sub_selector, radio, map_style)) + [1]


@app.callback(
    [dash.dependencies.Output(component_id={'type': 'dynamic-map', 'index': 2}, component_property='figure'),
     dash.dependencies.Output(component_id={'type': 'dynamic-sdd', 'index': 2}, component_property='options'),
     dash.dependencies.Output(component_id={'type': 'dynamic-sdd', 'index': 2}, component_property='style')],
    [dash.dependencies.Input(component_id="map_update", component_property='data'),
     dash.dependencies.Input(component_id={'type': 'dynamic-dd', 'index': 2}, component_property='value'),
     dash.dependencies.Input(component_id={'type': 'dynamic-sdd', 'index': 2}, component_property='value')],
    [dash.dependencies.State(component_id="menu_state", component_property='data'),
     dash.dependencies.State(component_id="slider_world_map", component_property='value'),
     dash.dependencies.State(component_id="radio_world_map", component_property='value'),
     dash.dependencies.State(component_id="map_style", component_property='value')]
)
def update_map2(map_update, selector, sub_selector, state, date_option, radio, map_style):
    if state:
        raise dash.exceptions.PreventUpdate
    return update_map(date_option, selector, sub_selector, radio, map_style)[:3]


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    pd.options.display.max_columns = None

    # Dash webserver setup
    app.run_server(host="127.0.0.1", port=6060, debug=False)
