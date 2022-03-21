import pandas as pd
import sqlite3
from db.db_dir import _starting_dir
from dash import Dash, Input, Output, html, dcc
import plotly.express as px

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

mean_total_city = data.groupby(["miasto", "data"])["Total"].mean()

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Interactive normal distribution'),

    html.P("Miasto:"),

    dcc.Dropdown(
        data["miasto"].unique(),
        placeholder="Select a city",
        id = "city"),

    dcc.DatePickerSingle(
        id='my-date-picker-single',
        disabled_days = ['2022-03-25', '2022-03-26']
    ),

    dcc.Graph(id="graph"),
])

@app.callback(
    Output("graph", "figure"),
    Input("city", "value"),

)
def display_hist(city):
    dataa = data[data["miasto"] == city] # replace with your own data source
    fig = px.histogram(dataa, x=dataa["Total"])
    return fig

app.run_server(debug=True)

if __name__ == "__main__":
    app.run_server(debug=True)
