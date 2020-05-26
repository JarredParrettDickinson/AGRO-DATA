import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.layout = html.Div([

    dcc.Dropdown(id='segselect', options=[{'label': 'A', 'value': 'A'},
                                          {'label': 'B', 'value': 'B'}]),

    html.Div(dcc.Slider(id='A', min=0, max=10, step=1), id='SliderAContainer'),
    html.Div(dcc.Slider(id='B', min=0, max=10, step=1, value=2), id='SliderBContainer'),
    dcc.Graph(id='plot_graph')

])   

@app.callback(Output('SliderAContainer', 'style'),
              [Input('segselect', 'value')])
def return_containerA(seg):
    if seg == 'A':
        return {}
    else:
        return {'display': 'none'}

@app.callback(Output('SliderBContainer', 'style'),
              [Input('segselect', 'value')])
def return_containerB(seg):
    if seg == 'B':
        return {}
    else:
        return {'display': 'none'}

if __name__ == "__main__":
    app.run_server(debug=True)