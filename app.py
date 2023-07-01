import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Load the aggregated dataset
aggregated_data = pd.read_csv('data/agg_cd_data.csv')

# Load the unaggregated dataset
unaggregated_data = pd.read_csv('data/unagg_tweet.csv', lineterminator='\n')

# Create Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1('Analysis Page'),
    dcc.Graph(id='cd-map', clickData={'points': [{'customdata': 'cd1'}]}),
    dcc.Graph(id='sentiment-pie'),
])

# Define callbacks
@app.callback(
    Output('sentiment-pie', 'figure'),
    [Input('cd-map', 'clickData')]
)
def update_sentiment_pie(clickData):
    if clickData is None:
        filtered_data = unaggregated_data
    else:
        selected_cd = clickData['points'][0]['customdata']
        filtered_data = unaggregated_data[unaggregated_data['CD'] == selected_cd]
    sentiment_counts = filtered_data['sentiment'].value_counts()
    fig = go.Figure(data=[go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values)])
    return fig

@app.callback(
    Output('cd-map', 'figure'),
    [Input('sentiment-pie', 'clickData')]
)
def update_cd_map(clickData):
    if clickData is None:
        filtered_data = aggregated_data
    else:
        selected_sentiment = clickData['points'][0]['label']
        filtered_data = aggregated_data[aggregated_data['AggregatedMetric'] == selected_sentiment]
    fig = px.choropleth_mapbox(
        filtered_data,
        geojson=filtered_data['the_geom'],
        locations=filtered_data['CD'],
        #color='AggregatedMetric',
        #color_continuous_scale='Viridis',
        mapbox_style='carto-positron',
        center={'lat': 40.7128, 'lon': -74.0060},
        zoom=10,
        opacity=0.5,
        labels={'AggregatedMetric': 'Metric'},
        hover_data={
            'shape_len': filtered_data['Shape_Leng'],
            'shape_area': filtered_data['Shape_Area']
        },
        hover_name='CD',
        title='Community Districts',
    )
    fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>Shape Length: %{customdata[0]:.2f}<br>Shape Area: %{customdata[1]:.2f}')
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
