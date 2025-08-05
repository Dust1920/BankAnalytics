from dash import Dash
from dash import html, dcc
from dash import callback, Input, Output


app = Dash()
app.title = "Finance App"

app.layout = html.Div([
    html.Header(children=[
        html.H1("Finance App",
                className="principal-title"),
    ]),
    html.Div(children=[
        dcc.Tabs(
            id="tabs", children=[
                dcc.Tab(label="Portfoly", children=[
                    html.Div(children=[

                    ])
                ]),
                dcc.Tab(label="IFM", children=[
                    html.Div(children=[

                    ])
                ]),
                dcc.Tab(label="Expenses", children=[
                    html.Div(children=[

                    ])
                ])
            ]
        )
    ]),
    html.Footer(children=[
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
