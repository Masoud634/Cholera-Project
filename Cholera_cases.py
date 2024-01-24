import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px

# Step 1: Load your data
data_copy = pd.read_csv('analyzed_data.csv')

# Step 2: Create Dash app
app = dash.Dash(__name__)

# Styling colors
colors = {
    'background': '#e6f7ff',  # Light blue
    'text': '#333333',
    'card': '#ffffff',  # White
}

# Step 3: Define the layout
app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '20px', 'font-family': 'Arial, sans-serif'}, children=[
    html.A(
        html.Img(src='https://upload.wikimedia.org/wikipedia/commons/c/c9/Linkedin.svg', height='50px', width='50px'),
        href='https://www.linkedin.com/in/masoud-bakhit17/',
        target='_blank',  # Open in a new tab
        style={'display': 'inline-block', 'margin-right': '20px'}
    ),
    
    dcc.Graph(
        id='geographic-heatmap',
        style={'height': '70vh', 'width': '100%', 'text-align': 'center', 'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'},
        config={'scrollZoom': False},
    ),
    
    html.Div(id='selected-country', style={'color': colors['text'], 'fontSize': 18, 'margin-top': '20px'}),
    
    html.Div([
        html.Div([
            dcc.Graph(id='avg-reported-cases-card'),
        ], style={'display': 'inline-block', 'width': '30%', 'border': '1px solid #ddd', 'padding': '10px', 'border-radius': '5px', 'background-color': colors['card'], 'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}),
        
        html.Div([
            dcc.Graph(id='avg-reported-deaths-card'),
        ], style={'display': 'inline-block', 'width': '30%', 'margin-left': '20px', 'border': '1px solid #ddd', 'padding': '10px', 'border-radius': '5px', 'background-color': colors['card'], 'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}),
        
        html.Div([
            dcc.Graph(id='avg-case-fatality-rate-card'),
        ], style={'display': 'inline-block', 'width': '30%', 'margin-left': '20px', 'border': '1px solid #ddd', 'padding': '10px', 'border-radius': '5px', 'background-color': colors['card'], 'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}),
    ], id='cards-container', style={'margin-top': '20px', 'text-align': 'center'}),

    dcc.Graph(id='line-chart', style={'width': '100%', 'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}),
])

# Step 4: Define callbacks
@app.callback(
    Output('selected-country', 'children'),
    [Input('geographic-heatmap', 'clickData')]
)
def display_selected_country(clickData):
    if clickData is None:
        return "Click on a country from the map to display results."
    
    selected_country = clickData['points'][0]['location']
    
    # Calculate the sum of reported cases of cholera for the selected country
    result_value = data_copy[data_copy['Country'] == selected_country]['Number of reported cases of cholera'].sum()
    
    result = f"Total reported cases of cholera in {selected_country}: {result_value}"
    
    return result

@app.callback(
    Output('avg-reported-cases-card', 'figure'),
    Output('avg-reported-deaths-card', 'figure'),
    Output('avg-case-fatality-rate-card', 'figure'),
    Output('line-chart', 'figure'),
    [Input('geographic-heatmap', 'clickData')]
)
def update_charts(clickData):
    if clickData is None:
        return {}, {}, {}, {}

    selected_country = clickData['points'][0]['location']
    country_data = data_copy[data_copy['Country'] == selected_country]

    avg_reported_cases = country_data['Number of reported cases of cholera'].mean().astype(int)
    avg_reported_deaths = country_data['Number of reported deaths from cholera'].mean().astype(int)
    avg_case_fatality_rate = country_data['Cholera case fatality rate'].mean()

    fig_avg_cases = go.Figure(go.Indicator(
        mode="number+delta",
        value=avg_reported_cases,
        title="Average Reported Cases",
        delta={'reference': avg_reported_cases.mean(), 'position': "top"},
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font': {'color': colors['text']}},
    ))
    
    fig_avg_deaths = go.Figure(go.Indicator(
        mode="number",
        value=avg_reported_deaths,
        title="Average Reported Deaths",
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font': {'color': colors['text']}},
    ))
    
    fig_avg_case_fatality_rate = go.Figure(go.Indicator(
        mode="number",
        value=avg_case_fatality_rate,
        title="Average Case Fatality Rate",
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font': {'color': colors['text']}},
    ))

    fig_line_chart = px.line(
        country_data,
        x='Year',
        y=['Number of reported cases of cholera', 'Number of reported deaths from cholera'],
        labels={'value': 'Count', 'variable': 'Category'},
        title=f'Reported Cases and Deaths Over Years ({selected_country})',
        line_shape='linear',
        template='plotly',
    )

    return fig_avg_cases, fig_avg_deaths, fig_avg_case_fatality_rate, fig_line_chart

# Step 5: Rank the degrees of the heatmap based on the specified condition
data_sorted = data_copy.groupby('Country')['Number of reported cases of cholera'].sum().reset_index()
data_sorted = data_sorted.sort_values(by='Number of reported cases of cholera', ascending=False)

# Step 6: Create a geographic heatmap with custom colors
fig = px.choropleth(
    data_sorted,
    locations='Country',
    locationmode='country names',
    color='Number of reported cases of cholera',
    color_continuous_scale="blues",  # Dark blue color scale
    title='Geographic Heatmap - Cholera Cases',
    labels={'Number of reported cases of cholera': 'Number of reported cases of cholera'},
)

# Step 7: Update the layout with the geographic heatmap
app.layout['geographic-heatmap'].figure = fig

# Step 8: Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
