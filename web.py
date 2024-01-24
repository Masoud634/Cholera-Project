import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px

# Step 1: Load your data
data_copy = pd.read_csv('analyzed_data.csv')

# Step 2: Create Dash app
app = dash.Dash(__name__)

# Step 3: Define the layout
app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='geographic-heatmap',
            config={'scrollZoom': False},
        ),
    ], style={'display': 'inline-block', 'width': '70%'}),
    
    html.Div([
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in data_copy['Country'].unique()],
            value=data_copy['Country'].iloc[0],  # Set default value to the first country
            style={'width': '100%'},
        ),
        
        # Hidden div to store selected country
        html.Div(id='selected-country-hidden', style={'display': 'none'}),
        
        html.Div(id='selected-country'),
    ], style={'display': 'inline-block', 'width': '30%', 'margin-left': '20px'}),
])

# Step 4: Define callbacks
@app.callback(
    [Output('selected-country-hidden', 'children'),
     Output('selected-country', 'children'),
     Output('geographic-heatmap', 'figure'),
     Output('country-dropdown', 'value')],
    [Input('geographic-heatmap', 'clickData'),
     Input('country-dropdown', 'value')],
    State('geographic-heatmap', 'figure')
)
def display_selected_country(clickData, selected_country_dropdown, current_figure):
    ctx = dash.callback_context
    triggered_id = ctx.triggered_id
    if triggered_id and 'geographic-heatmap' in triggered_id:
        # Clicked on the map
        selected_country = clickData['points'][0]['location']
    elif selected_country_dropdown:
        # Selected from the dropdown
        selected_country = selected_country_dropdown
    else:
        return None, "Click on a country or choose from the dropdown to display results.", current_figure, data_copy['Country'].iloc[0]
    
    # Calculate the sum of reported cases of cholera for the selected country
    result_value = data_copy[data_copy['Country'] == selected_country]['Number of reported cases of cholera'].sum()
    
    result = f"Total reported cases of cholera in {selected_country}: {result_value}"
    
    # Highlight the selected country without zooming
    highlighted_figure = px.choropleth(
        data_copy,
        locations='Country',
        locationmode='country names',
        color='Number of reported cases of cholera',
        color_continuous_scale="reds",
        title=f'Geographic Heatmap - Cholera Cases (Selected: {selected_country})',
        labels={'Number of reported cases of cholera': 'Number of reported cases of cholera'},
    )
    
    # Set the selected country color to stand out
    highlighted_figure.update_traces(marker_line_color='black', marker_line_width=2, selector=dict(name=selected_country))
    
    return selected_country, result, highlighted_figure, selected_country

# Step 5: Rank the degrees of the heatmap based on the specified condition
data_sorted = data_copy.groupby('Country')['Number of reported cases of cholera'].sum().reset_index()
data_sorted = data_sorted.sort_values(by='Number of reported cases of cholera', ascending=False)

# Step 6: Create an initial geographic heatmap
initial_figure = px.choropleth(
    data_sorted,
    locations='Country',
    locationmode='country names',
    color='Number of reported cases of cholera',
    color_continuous_scale="reds",
    title='Geographic Heatmap - Cholera Cases (Ranked)',
    labels={'Number of reported cases of cholera': 'Number of reported cases of cholera'},
)

# Step 7: Update the layout with the initial geographic heatmap
app.layout['geographic-heatmap'].figure = initial_figure

# Step 8: Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
