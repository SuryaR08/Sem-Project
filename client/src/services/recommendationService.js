import axios from "axios";

export const getRecommendedRoutes = async (date) => {
  try {
    const response = await axios.post("http://127.0.0.1:5000/recommend-routes", { date });
    return response.data.recommended_routes || [];
  } catch (error) {
    console.error("Error fetching recommended routes:", error);
    throw error;
  }
};
