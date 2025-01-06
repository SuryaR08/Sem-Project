from flask import Flask, jsonify, request
from recommendation_logic import recommend_routes

app = Flask(__name__)

@app.route('/recommend-routes', methods=['POST'])
def recommend_routes_api():
    data = request.json  # Expecting JSON input like: {"date": "2025-01-01"}
    if not data or 'date' not in data:
        return jsonify({"error": "Missing 'date' parameter"}), 400

    date = data['date']
    try:
        routes = recommend_routes(date)
        return jsonify({"recommended_routes": routes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
