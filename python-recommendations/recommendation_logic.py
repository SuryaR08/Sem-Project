import pandas as pd
import numpy as np
import json
import networkx as nx
from geopy.distance import geodesic
from statsmodels.tsa.arima.model import ARIMA

# Load data
def load_data():
    # Load garbage bin data
    garbage_data = pd.read_csv('data/garbage_data.csv')
    with open('data/city_graph.json', 'r') as f:
        city_graph = json.load(f)
    return garbage_data, city_graph

# ARIMA-based prediction for garbage levels
def predict_garbage_levels(date, garbage_data):
    predictions = []
    areas = garbage_data['area'].unique()
    for area in areas:
        area_data = garbage_data[garbage_data['area'] == area]
        area_series = area_data['garbage_level']

        # Fit ARIMA model
        model = ARIMA(area_series, order=(1, 1, 1))
        model_fit = model.fit()
        prediction = model_fit.forecast(steps=1)[0]
        predictions.append({"area": area, "predicted_garbage_level": prediction})
    
    return predictions

# Find shortest routes based on garbage levels
def find_shortest_routes(predictions, city_graph):
    # Filter high-priority bins
    high_priority_bins = [
        pred for pred in predictions if pred['predicted_garbage_level'] > 80
    ]

    # Use NetworkX to calculate shortest routes
    G = nx.Graph()
    for edge in city_graph['edges']:
        G.add_edge(edge['from'], edge['to'], weight=edge['distance'])

    routes = []
    for bin_info in high_priority_bins:
        area = bin_info['area']
        shortest_path = nx.shortest_path(G, source="depot", target=area, weight="weight")
        total_distance = sum(
            G[shortest_path[i]][shortest_path[i+1]]['weight']
            for i in range(len(shortest_path) - 1)
        )
        routes.append({"route": shortest_path, "total_distance": total_distance})

    return sorted(routes, key=lambda x: x['total_distance'])

# Main recommendation function
def recommend_routes(date):
    garbage_data, city_graph = load_data()
    predictions = predict_garbage_levels(date, garbage_data)
    routes = find_shortest_routes(predictions, city_graph)
    return routes
