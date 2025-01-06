import pandas as pd
import networkx as nx
from statsmodels.tsa.arima.model import ARIMA
from geopy.distance import geodesic
import json
import numpy as np

def load_data():
    garbage_data = pd.read_csv('data/garbage_data.csv')
    with open('data/city_graph.json', 'r') as f:
        city_graph = json.load(f)
    return garbage_data, city_graph

def predict_garbage_levels(date, garbage_data):
    predictions = []
    areas = garbage_data['area'].unique()
    
    for area in areas:
        area_data = garbage_data[garbage_data['area'] == area]
        
        # Simulating garbage levels if data is insufficient
        if len(area_data) < 5:
            prediction = np.random.randint(20, 70)  # Simulated range of garbage levels
        else:
            try:
                # Extracting the garbage level time series
                area_series = area_data['garbage_level']
                
                # Using ARIMA model for prediction
                model = ARIMA(area_series, order=(1, 1, 1))  # Tuned parameters
                model_fit = model.fit()
                
                # Predicting the next day's garbage level
                prediction = model_fit.forecast(steps=1)[0]
            except Exception as e:
                print(f"ARIMA error for area {area}: {e}")
                prediction = 50  # Default fallback prediction
                
        predictions.append({"area": area, "predicted_garbage_level": round(prediction, 2)})
    
    print(f"Predictions for {date}: {predictions}")
    return predictions

def find_shortest_routes(predictions, city_graph):
    # Filtering bins with high predicted garbage levels (threshold > 40)
    high_priority_bins = [pred for pred in predictions if pred['predicted_garbage_level'] > 40]
    
    # Create graph using NetworkX
    G = nx.Graph()
    for edge in city_graph['edges']:
        G.add_edge(edge['from'], edge['to'], weight=edge['distance'])
    
    routes = []
    for bin_info in high_priority_bins:
        area = bin_info['area']
        try:
            # Finding the shortest path from the depot to the high-priority area
            shortest_path = nx.shortest_path(G, source="depot", target=area, weight="weight")
            
            # Calculating the total distance of the route
            total_distance = sum(G[shortest_path[i]][shortest_path[i + 1]]['weight'] for i in range(len(shortest_path) - 1))
            
            # Adding the route details
            routes.append({
                "area": area,
                "route": shortest_path,
                "total_distance": round(total_distance, 2),
                "predicted_garbage_level": bin_info['predicted_garbage_level']
            })
        except nx.NetworkXNoPath:
            print(f"No path found to area {area}")
    
    # Sorting routes by total distance (ascending) and garbage level (descending priority)
    routes = sorted(routes, key=lambda x: (x['total_distance'], -x['predicted_garbage_level']))
    return routes

def recommend_routes(date):
    # Load the dataset and graph
    garbage_data, city_graph = load_data()
    
    # Predict garbage levels for each area
    predictions = predict_garbage_levels(date, garbage_data)
    
    # Find and prioritize shortest routes to high-priority bins
    routes = find_shortest_routes(predictions, city_graph)
    
    # Display recommended routes
    print(f"Recommended routes for {date}:")
    for route in routes:
        print(f"Route to {route['area']}: {route['route']} with distance {route['total_distance']} km")
    
    return routes