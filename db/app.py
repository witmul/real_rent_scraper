import pandas as pd
import sqlite3
#from db.db_dir import _starting_dir
from db_dir import _starting_dir
from dash import Dash, Input, Output, html, dcc, dash_table

import plotly.graph_objects as go
from plotly.subplots import make_subplots

#<====================== Connect to the database
conn = sqlite3.connect(_starting_dir() + "\db_flats.db")

#<====================== Run SQL
sql_query = pd.read_sql('SELECT * FROM flats_rent', conn)
sql_query["data"] = pd.to_datetime(sql_query["data"], format="%Y-%m-%d")
sql_query = sql_query.dropna(subset=["Total"])
sql_query["Total"] = sql_query["Total"].astype(int)

#<====================== Cleaning data
empty_df = pd.DataFrame()

for city in sql_query["miasto"].unique():
    city_df = sql_query[sql_query["miasto"] == city]
    for date in city_df["data"].unique():
        city_df_date = city_df[city_df["data"] == date]
        city_df_date = city_df_date.drop_duplicates()
        empty_df = empty_df.append(city_df_date)

empty_df.rename(columns = {'Names':'Description',
                           'Add_cost':'Additional_cost',
                           'Num of rooms':'Rooms_Number',
                           'data':'Load_Date',
                           'miasto':'City'},
                inplace = True)

data = empty_df[["Description", "City", "Price", "Additional_cost", "Total", "Rooms_Number", "Size", "zl/m2", "Load_Date"]]
data = data[data["Total"] < 15000].copy() # need to limit amount of flats / copy just to remove error
data['Load_Date'] = pd.to_datetime(data['Load_Date']).dt.date
#data["Num of rooms"].unique()

#########################
#Add num of rooms option#
#########################
#<====================== Dash App

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Real Rent App!"

#app = Dash(__name__)

app.layout = html.Div(
    children=[
        dcc.Tabs([
                dcc.Tab(label='Tab one', children=[

                        html.Div(children=[
                            html.H1(children='Real Rent Scraper Results:',
                                    className="header-title"),
                        ]
                        ),
                        html.Div(children=[
                            html.Div(children=[
                                html.Br(),
                                html.Label('Please select a city:',
                                            className="menu-title"),
                                dcc.Dropdown(
                                    data["City"].unique(),
                                    value=data["City"].unique()[0],
                                    multi=False,
                                    id="city")
                            ]
                            ),
                            html.Div(children=[
                                html.Br(),
                                html.Label('Please select min and max prices for rent:',
                                           className="menu-title"),
                                dcc.RangeSlider(0,
                                                max(data["Total"]),
                                                value=[500, 5000],
                                                tooltip={"placement": "bottom", "always_visible": True},
                                                id="range-slider")
                            ]
                            ),
                        ],
                        className="menu",
                        ),
                        dcc.Graph(id="histogram",
                                  className="card"),
                        dcc.Graph(id="line",
                                  className="card"),
                    ]

                ),
            dcc.Tab(label='Tab two', children=[

                html.Div(children=[
                    html.H1(children='Real Rent Scraper Results:',
                            className="header-title"),
                ]),
            ])],
        )],
    className="wrapper",
)
#<====================== Histogram Callback
@app.callback(
    Output("histogram", "figure"),
    Input("city", "value"),
    Input("range-slider", "value")
)
def display_hist(city, price):
    #dataa = data[data["miasto"].isin([city])]
    dataa = data[data["City"] == city]
    dataa = dataa[dataa["Total"].between(price[0], price[1])]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=dataa["Total"].tolist(),
        name='flats',
        xbins=dict(
            start=price[0],
            end=price[1],
            size=100
        ),
        marker_color='#00a8a8',
        opacity=0.75
        # name used in legend and hover labels
    ))

    fig.update_layout(
        title_text='Rent Prices Results',  # title of plot
        xaxis_title_text='Price in PLN per month',  # xaxis label
        yaxis_title_text='Number of flats',  # yaxis label
        bargap=0.05,  # gap between bars of adjacent location coordinates
        #bargroupgap=0.1  # gap between bars of the same location coordinates
    )

    return fig

#<====================== Line Graph Callback
@app.callback(
    Output("line", "figure"),
    Input("city", "value"),
    Input("range-slider", "value")
)
def display_line(city, price):
    dataa = data[data["City"] == city]
    #dataa = data[data["miasto"].isin([city])]
    dataa = dataa[dataa["Total"].between(price[0], price[1])]

    mean_total_city = dataa.groupby(["City", "Load_Date"])["Total"].mean()
    count_total_city = dataa.groupby(["City", "Load_Date"])["Description"].count()

    data_mean = mean_total_city[city].to_frame() #should include city to avoid multyindexing
    data_count = count_total_city[city].to_frame()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=data_mean.index.tolist(),
                   y=data_mean.iloc[:, 0],
                   name="Mean rent price per month",
                   mode='lines',
                   marker_color='#00d6d6'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=data_count.index.tolist(),
                   y=data_count.iloc[:, 0],
                   name="Number of unique offers on the platform",
                   mode='lines',
                   marker_color='#651a1a'),
        secondary_y=True,
    )

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Mean rent price per month in PLN", secondary_y=False)
    fig.update_yaxes(title_text="Number of unique offers on the platform", secondary_y=True)

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
