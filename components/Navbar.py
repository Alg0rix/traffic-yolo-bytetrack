from dash import Input, Output, dcc, html
import dash
import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


# Define the navbar structure
def navbar():
    layout = html.Div(
        [
            html.H2("Menu", className="display-4"),
            html.Hr(),
            html.P("Navigate through the app", className="lead"),
            dbc.Nav(
                children=[
                    dbc.NavItem(dbc.NavLink("Home", href="/home")),
                    # dropdown nav
                    dbc.NavItem(
                        children=[
                            dbc.NavLink("Camera", href="/camera"),
                            dbc.NavLink("Traffic", href="/traffic"),
                        ],
                    ),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )

    return layout
