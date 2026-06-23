import React, { useState, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchTop = async () => {
    const res = await axios.get("/api/top");
    setProjects(Array.isArray(res.data) ? res.data : []);
  };

  const manualScan = async () => {
    setLoading(true);
    await axios.post("/api/manual-scan");
    await fetchTop();
    setLoading(false);
  };

  useEffect(() => {
    fetchTop();
  }, []);

  return (
    <div style={{ padding: 40, fontFamily: "Arial" }}>
      <h1>🚀 Retro Intelligence V4</h1>

      <button
        onClick={manualScan}
        style={{
          padding: "10px 20px",
          marginBottom: "20px",
          cursor: "pointer"
        }}
      >
        {loading ? "Scanning..." : "Manual Funding Scan"}
      </button>

      <table border="1" cellPadding="8" cellSpacing="0">
        <thead>
          <tr>
            <th>Name</th>
            <th>Chain</th>
            <th>Funding</th>
            <th>Score</th>
            <th>Retro %</th>
            <th>Capital</th>
            <th>Sybil Risk</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((p, idx) => (
            <tr key={idx}>
              <td>{p.name}</td>
              <td>{p.chain}</td>
              <td>${p.funding}</td>
              <td>{p.score}</td>
              <td>{(p.retro_probability * 100).toFixed(1)}%</td>
              <td>${p.capital_required}</td>
              <td>{p.sybil_risk}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}