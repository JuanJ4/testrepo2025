import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Cargar el conjunto de datos
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Obtener los sitios de lanzamiento únicos
launch_sites = spacex_df['Launch Site'].unique()

# Obtener el rango de carga útil
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Definir el layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', 
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Menú desplegable (Tarea 1)
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True,
        style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
    ),
    
    # Gráfico circular (Tarea 2)
    html.Div(dcc.Graph(id='success-pie-chart'), style={'margin-top': 20}),
    
    # Control deslizante (Tarea 3)
    html.Div([
        html.Label('Payload Mass Range (kg):', style={'font-size': '18px', 'margin-top': '20px'}),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={0: '0 kg', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
            value=[min_payload, max_payload]
        )
    ], style={'width': '80%', 'margin-top': '20px', 'margin-left': 'auto', 'margin-right': 'auto'}),
    
    # Gráfico de dispersión (Tarea 4)
    html.Div(dcc.Graph(id='success-payload-scatter-chart'), style={'margin-top': '20px'})
])

# Callback para el gráfico circular
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        data = spacex_df['class'].value_counts().reset_index()
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        data = filtered_df['class'].value_counts().reset_index()
    
    data.columns = ['Outcome', 'Count']
    data['Outcome'] = data['Outcome'].map({1: 'Success', 0: 'Failure'})
    if 'Success' not in data['Outcome'].values:
        data = pd.concat([data, pd.DataFrame({'Outcome': ['Success'], 'Count': [0]})], ignore_index=True)
    if 'Failure' not in data['Outcome'].values:
        data = pd.concat([data, pd.DataFrame({'Outcome': ['Failure'], 'Count': [0]})], ignore_index=True)
    
    fig = px.pie(data, values='Count', names='Outcome', 
                 title=f'Total Launch Successes ({entered_site if entered_site != "ALL" else "All Sites"})')
    return fig

# Callback para el gráfico de dispersión
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'), Input('payload-slider', 'value')]
)
def get_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='class',
                     labels={'class': 'Launch Outcome (0=Failure, 1=Success)'},
                     title=f'Payload vs. Launch Outcome ({entered_site if entered_site != "ALL" else "All Sites"})',
                     color_continuous_scale=['red', 'green'])
    fig.update_layout(yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Failure', 'Success']))
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True, port=8051)
