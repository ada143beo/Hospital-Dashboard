import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# Use Flatly theme
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.FLATLY]
)
server = app.server
 
app.layout = html.Div([

    dcc.Location(id="url"),

    # NAVBAR
    dbc.Navbar(
        dbc.Container([


            dbc.NavbarBrand(
                html.Div([
                    html.Img(src="/assets/logo.jpg", height="50px", className="rounded-circle me-3"),
                    html.Span("General Hospital Dashboard", className="fw-bold fs-3 text-uppercase")
                ], className="d-flex align-items-center")
            ),

            dbc.NavbarToggler(id="navbar-toggler"),

            dbc.Collapse(
                dbc.Nav(
                    id="nav-links",
                    navbar=True,
                    className="ms-auto",
                ),
                id="navbar-collapse", 
                navbar=True,
            ),

        ], fluid=True, className="mx-4"),
        color="#004f04",  
        style={"boxShadow": "0 2px 8px #000000"}, 
        fixed="top", className="py-4"
    ),

    # PAGE CONTENT
    dbc.Container(
        children=[dash.page_container],
        fluid=True,
        className="mt-5 pt-5",
        style={"backgroundColor": "#f2fcf5", "minHeight": "100vh"}
    )

])

@app.callback(
    Output("nav-links", "children"),
    Input("url", "pathname")
)

def update_nav(pathname):
    links = []
    for page in dash.page_registry.values():
        is_active = pathname == page["path"]

        links.append(
            dbc.NavLink(
                page["name"],
                href=page["path"],
                active=is_active,
                className="px-3 fs-6 mx-1",
                style={
                    "backgroundColor": "white" if is_active else "transparent",
                    "color": "#004f04" if is_active else "white",
                    "borderRadius": "8px",
                    "fontWeight": "bold" if is_active else "normal",
                    "transition": "all 0.3s ease" 
                }

            )
        )
    return links

@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_navbar(n, is_open):
    if n:
        return not is_open  
    return is_open


if __name__ == '__main__':
    app.run(debug=False)
