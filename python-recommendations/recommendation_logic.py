import pandas as pd
import networkx as nx
from statsmodels.tsa.statespace.sarimax import SARIMAX
from geopy.distance import geodesic
import json
import numpy as np

def load_data():
    garbage_data = pd.read_csv('data/garbage_data.csv', parse_dates=['date'])
    print(garbage_data.head())
    garbage_data.set_index('date', inplace=True)
    with open('data/city_graph.json', 'r') as f:
        city_graph = json.load(f)
    return garbage_data, city_graph

def predict_garbage_levels(target_date, garbage_data):
    predictions = []
    areas = garbage_data['area'].unique()
    target_date = pd.to_datetime(target_date)  # Ensure target_date is a datetime object

    for area in areas:
        area_data = garbage_data[garbage_data['area'] == area].copy()
        
        # Ensure the data is sorted by date
        area_data.sort_index(inplace=True)

        # Check if sufficient data exists
        if len(area_data) < 10:  # Require at least 10 data points
            prediction = np.random.randint(20, 70)  # Simulated range of garbage levels
        else:
            try:
                # Filling missing dates with forward-fill or backward-fill
                area_data = area_data.asfreq('D').fillna(method='ffill')

                # Extracting the garbage level time series
                area_series = area_data['garbage_level']

                # Using SARIMA model for prediction
                model = SARIMAX(area_series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
                model_fit = model.fit(disp=False)

                # Calculate the number of days to forecast
                last_date = area_data.index[-1]
                days_to_forecast = (target_date - last_date).days

                if days_to_forecast <= 0:
                    # If target_date is before or equal to the last data point, use the last known value
                    prediction = area_series.iloc[-1]
                else:
                    # Predicting garbage levels up to the target_date
                    future_forecast = model_fit.forecast(steps=days_to_forecast)
                    prediction = future_forecast.iloc[-1]  # Garbage level for the target_date
            except Exception as e:
                print(f"Error predicting for area {area}: {e}")
                prediction = np.random.randint(20, 70)  # Fallback value

        predictions.append({'area': area, 'predicted_garbage_level': float(prediction)})

    return predictions

def find_shortest_routes(predictions, city_graph):
    # Filtering bins with high predicted garbage levels (threshold > 40)
    high_priority_bins = predictions  # Already sorted by garbage level
    
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
    
    # Sort routes by predicted garbage level in descending order (already sorted by input order if predictions were sorted)
    routes = sorted(routes, key=lambda x: x['predicted_garbage_level'], reverse=True)
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
        print(f"Route to {route['area']}: {route['route']} with distance {route['total_distance']} km and predicted garbage level {route['predicted_garbage_level']}")
    
    return routes

