import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import networkx as nx
from geopy.distance import geodesic

# Step 1: Dummy Data Simulation
def generate_dummy_data(num_bins=10, time_steps=24):
    """
    Simulate dummy garbage level data for bins across different areas.
    :param num_bins: Number of garbage bins.
    :param time_steps: Number of time steps (hours).
    :return: DataFrame containing bin IDs, coordinates, and garbage levels.
    """
    data = []
    np.random.seed(42)
    
    for bin_id in range(1, num_bins + 1):
        lat = 13.08 + np.random.uniform(-0.02, 0.02)
        lon = 80.27 + np.random.uniform(-0.02, 0.02)
        levels = np.cumsum(np.random.uniform(5, 10, size=time_steps)) % 100  # Random garbage levels
        for t, level in enumerate(levels):
            data.append((bin_id, lat, lon, t, level))

    return pd.DataFrame(data, columns=['BinID', 'Latitude', 'Longitude', 'Time', 'GarbageLevel'])

# Generate dummy data
df_bins = generate_dummy_data()

# Step 2: ARIMA Prediction
def predict_garbage_levels(df, steps_ahead=6):
    """
    Predict future garbage levels using ARIMA.
    :param df: DataFrame with garbage levels.
    :param steps_ahead: Number of steps to predict.
    :return: DataFrame with predictions.
    """
    predictions = []

    for bin_id in df['BinID'].unique():
        bin_data = df[df['BinID'] == bin_id]
        levels = bin_data['GarbageLevel'].values

        try:
            model = ARIMA(levels, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=steps_ahead)
            predictions.append((bin_id, forecast[-1]))
        except Exception as e:
            print(f"Error for Bin {bin_id}: {e}")

    return pd.DataFrame(predictions, columns=['BinID', 'PredictedLevel'])

# Predict future garbage levels
df_predictions = predict_garbage_levels(df_bins)

# Step 3: Prioritization
def prioritize_bins(df_predictions, threshold=80):
    """
    Prioritize bins based on predicted garbage levels.
    :param df_predictions: DataFrame with predictions.
    :param threshold: Garbage level threshold for prioritization.
    :return: List of prioritized bin IDs.
    """
    return df_predictions[df_predictions['PredictedLevel'] >= threshold]['BinID'].tolist()

# Get prioritized bins
prioritized_bins = prioritize_bins(df_predictions)

# Step 4: Route Optimization
def generate_shortest_route(df, prioritized_bins):
    """
    Generate shortest route for prioritized bins.
    :param df: DataFrame with bin data.
    :param prioritized_bins: List of prioritized bin IDs.
    :return: Optimized route (list of coordinates).
    """
    prioritized_data = df[df['BinID'].isin(prioritized_bins)].drop_duplicates('BinID')
    locations = prioritized_data[['Latitude', 'Longitude']].values

    # Create graph
    G = nx.Graph()
    
    for i, loc1 in enumerate(locations):
        for j, loc2 in enumerate(locations):
            if i != j:
                distance = geodesic(loc1, loc2).meters
                G.add_edge(i, j, weight=distance)

    # Find shortest path
    if locations.shape[0] > 1:
        path = nx.shortest_path(G, source=0, target=locations.shape[0] - 1, weight='weight')
        route = [locations[i] for i in path]
    else:
        route = locations.tolist()

    return route

# Generate shortest route
optimized_route = generate_shortest_route(df_bins, prioritized_bins)

# Step 5: Display Results
print("Prioritized Bins:", prioritized_bins)
print("Optimized Route:", optimized_route)
