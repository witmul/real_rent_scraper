import pandas as pd
import sqlite3
from db.db_dir import _starting_dir
from dash import Dash, Input, Output, html, dcc

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Connect to the database
conn = sqlite3.connect(_starting_dir() + "\db_flats.db")

# Run SQL
sql_query = pd.read_sql('SELECT * FROM flats_rent', conn)
sql_query["data"] = pd.to_datetime(sql_query["data"], format="%Y-%m-%d")
sql_query = sql_query.dropna(subset=["Total"])
sql_query["Total"] = sql_query["Total"].astype(int)

empty_df = pd.DataFrame()

for city in sql_query["miasto"].unique():
    city_df = sql_query[sql_query["miasto"] == city]
    for date in city_df["data"].unique():
        city_df_date = city_df[city_df["data"] == date]
        city_df_date = city_df_date.drop_duplicates()
        empty_df = empty_df.append(city_df_date)

data = empty_df[["Names", "miasto", "Price", "Add_cost", "Total", "Num of rooms", "Size", "zl/m2", "data"]]
data = data[data["Total"] < 8000]
data = data[data["Total"] > 200]

mean_total_city = data.groupby(["miasto", "data"])["Total"].mean()
count_total_city = data.groupby(["miasto", "data"])["Names"].count()

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Interactive normal distribution'),

    html.P("Miasto:"),

    dcc.Dropdown(
        data["miasto"].unique(),
        value=data["miasto"].unique()[0],
        #placeholder="Select a city",
        id = "city"),

    dcc.Graph(id="histogram"),
    dcc.Graph(id="line"),
])

@app.callback(
    Output("histogram", "figure"),
    Input("city", "value"),
)
def display_hist(city):
    dataa = data[data["miasto"] == city]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=dataa["Total"].tolist(),
        name='test',  # name used in legend and hover labels
    ))


    #fig = px.histogram(dataa, x=dataa["Total"], nbins = 50)
    return fig

@app.callback(
    Output("line", "figure"),
    Input("city", "value"),
)
def display_line(city):
    data_mean = mean_total_city[city].to_frame()
    data_count = count_total_city[city].to_frame()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=data_mean.index.tolist(),
                   y=data_mean.iloc[:, 0],
                   name="Srednia cena wynajmu mieszkania"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=data_count.index.tolist(),
                   y=data_count.iloc[:, 0],
                   name="Ogolna liczba ofert na platformie"),
        secondary_y=True,
    )

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
