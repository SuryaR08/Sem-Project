import React, { useState, useEffect } from "react";
import { createSchedule, deleteSchedule } from "../services/scheduleAllocationService";
import { getSchedules } from "../services/scheduleService";
import { getRecommendedRoutes } from "../services/recommendationService";
import "../ScheduleAllocation.css";

const ScheduleAllocation = () => {
  const [schedules, setSchedules] = useState([]);
  const [newSchedule, setNewSchedule] = useState({
    date: "",
    time: "",
    location: "",
  });
  const [recommendedRoutes, setRecommendedRoutes] = useState([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    try {
      const schedulesData = await getSchedules();
      setSchedules(schedulesData);
    } catch (error) {
      console.error("Error fetching schedules:", error);
    }
  };

  const handleDateTimeChange = async () => {
    if (newSchedule.date) {
      setLoadingRecommendations(true);
      try {
        const routes = await getRecommendedRoutes(newSchedule.date); // Call the API with the selected date
        setRecommendedRoutes(routes);
      } catch (error) {
        console.error("Error fetching recommended routes:", error);
      }
      setLoadingRecommendations(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const createdSchedule = await createSchedule(newSchedule);
      setSchedules([...schedules, createdSchedule]);
      setNewSchedule({ date: "", time: "", location: "" });
      setRecommendedRoutes([]); // Clear recommendations after submission
    } catch (error) {
      console.error("Error creating schedule:", error);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteSchedule(id);
      const updatedSchedules = schedules.filter((schedule) => schedule.id !== id);
      setSchedules(updatedSchedules);
    } catch (error) {
      console.error("Error deleting schedule:", error);
    }
  };

  return (
    <div className="schedule-allocation-container">
      <h2>Schedule Allocation</h2>
      <form onSubmit={handleSubmit} className="schedule-form">
        <div className="form-group">
          <label>Date:</label>
          <input
            type="date"
            value={newSchedule.date}
            onChange={(e) => {
              setNewSchedule({ ...newSchedule, date: e.target.value });
              handleDateTimeChange();
            }}
            required
          />
        </div>
        <div className="form-group">
          <label>Time:</label>
          <input
            type="time"
            value={newSchedule.time}
            onChange={(e) => {
              setNewSchedule({ ...newSchedule, time: e.target.value });
              handleDateTimeChange();
            }}
            required
          />
        </div>
        <div className="form-group">
          <label>Location:</label>
          <select
            value={newSchedule.location}
            onChange={(e) => setNewSchedule({ ...newSchedule, location: e.target.value })}
            required
          >
            <option value="" disabled>
              Select a location
            </option>
            {loadingRecommendations ? (
              <option>Loading recommendations...</option>
            ) : (
              recommendedRoutes.map((route, index) => (
                <option key={index} value={route.route.join(" -> ")}>
                  {route.route.join(" -> ")} (Total Distance: {route.total_distance} km, Garbage Level:{" "}
                  {route.predicted_garbage_level})
                </option>
              ))
            )}
          </select>
        </div>
        <button type="submit">Create Schedule</button>
      </form>

      <div className="schedule-list">
        {schedules.length > 0 ? (
          schedules.map((schedule) => (
            <div key={schedule.id} className="schedule-card">
              <p>
                <strong>Date:</strong> {schedule.date}
              </p>
              <p>
                <strong>Time:</strong> {schedule.time}
              </p>
              <p>
                <strong>Location:</strong> {schedule.location}
              </p>
              <button className="delete-button" onClick={() => handleDelete(schedule.id)}>
                Delete
              </button>
            </div>
          ))
        ) : (
          <p>No schedules available.</p>
        )}
      </div>
    </div>
  );
};

export default ScheduleAllocation;
