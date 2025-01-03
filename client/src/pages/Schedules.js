import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '../Schedules.css';
import { getSchedules } from '../services/scheduleService';

// Define garbage truck icon
const vanIconMarker = L.icon({
  iconUrl: '../img/van.png', // Example icon
  iconSize: [50, 50],
  iconAnchor: [25, 25],
});

// Define realistic paths (roads in Chennai)
const vanPaths = [
  [
    [13.0827, 80.2707],
    [13.0830, 80.2725],
    [13.0835, 80.2740],
    [13.0840, 80.2760],
  ],
  [
    [13.0850, 80.2740],
    [13.0852, 80.2750],
    [13.0855, 80.2765],
    [13.0860, 80.2780],
  ],
  [
    [13.0790, 80.2650],
    [13.0795, 80.2660],
    [13.0800, 80.2675],
    [13.0810, 80.2690],
  ],
];

// Utility function to interpolate between points
const interpolate = (start, end, fraction) => [
  start[0] + (end[0] - start[0]) * fraction,
  start[1] + (end[1] - start[1]) * fraction,
];

// Component to fit the map view dynamically
const FitToBounds = ({ paths }) => {
  const map = useMap();

  useEffect(() => {
    const allCoordinates = paths.flat();
    const bounds = L.latLngBounds(allCoordinates);
    map.fitBounds(bounds);
  }, [paths, map]);

  return null;
};

const Schedules = () => {
  const [schedules, setSchedules] = useState([]);
  const [vanLocations, setVanLocations] = useState(vanPaths.map((path) => path[0]));
  const [fractions, setFractions] = useState(vanPaths.map(() => 0));
  const [segmentIndices, setSegmentIndices] = useState(vanPaths.map(() => 0));
  const intervalRef = useRef(null);

  // Fetch schedules from the service
  useEffect(() => {
    const fetchSchedules = async () => {
      try {
        const schedulesData = await getSchedules();
        setSchedules(schedulesData);
      } catch (error) {
        console.error('Error fetching schedules:', error);
      }
    };

    fetchSchedules();
  }, []);

  // Simulate van movement
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setFractions((prevFractions) =>
        prevFractions.map((fraction, index) => {
          const currentPath = vanPaths[index];
          const currentSegmentIndex = segmentIndices[index];
          const nextFraction = fraction + 0.01; // Adjust speed here
          if (nextFraction >= 1) {
            // Move to the next segment
            if (currentSegmentIndex < currentPath.length - 2) {
              segmentIndices[index] = currentSegmentIndex + 1;
            } else {
              // Stop at the end of the path
              return 1;
            }
            return 0;
          }
          return nextFraction;
        })
      );

      setVanLocations((prevLocations) =>
        prevLocations.map((_, index) => {
          const currentPath = vanPaths[index];
          const currentSegmentIndex = segmentIndices[index];
          const start = currentPath[currentSegmentIndex];
          const end = currentPath[currentSegmentIndex + 1];
          return interpolate(start, end, fractions[index]);
        })
      );
    }, 100); // Update interval

    return () => clearInterval(intervalRef.current); // Cleanup on unmount
  }, [fractions, segmentIndices]);

  return (
    <div className="schedules-page">
      <h2>My Schedules</h2>
      <div className="schedule-list">
        {schedules.length > 0 ? (
          schedules.map((schedule) => (
            <div key={schedule.id} className="schedule-card">
              <h3>
                <strong>Date:</strong> {schedule.date}
              </h3>
              <p>
                <strong>Time:</strong> {schedule.time}
              </p>
              <p>
                <strong>Location:</strong> {schedule.location}
              </p>
            </div>
          ))
        ) : (
          <p>No schedules available.</p>
        )}
      </div>
      <div className="map-container">
        <MapContainer zoom={13} scrollWheelZoom={false} style={{ height: '500px', width: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <FitToBounds paths={vanPaths} />
          {vanPaths.map((path, index) => (
            <Polyline key={index} positions={path} color="blue" />
          ))}
          {vanLocations.map((location, index) => (
            <Marker key={index} position={location} icon={vanIconMarker}>
              <Popup>Garbage Van {index + 1} is here!</Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default Schedules;
