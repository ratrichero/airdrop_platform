import React, { useState, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [url, setUrl] = useState("");
  const [projects, setProjects] = useState([]);

  const fetchProjects = async () => {
    const res = await axios.get("/projects");
    console.log(res.data);
    setProjects(res.data);
  };
  

  const scan = async () => {
    await axios.post("/scan", null, { params: { url } });
    fetchProjects();
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Airdrop Scanner</h1>
      <input value={url} onChange={e => setUrl(e.target.value)} placeholder="Enter URL" />
      <button onClick={scan}>Scan</button>

      <table border="1" style={{ marginTop: 20 }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Chain</th>
            <th>Funding</th>
          </tr>
        </thead>
        <tbody>
          {projects?.length > 0 &&
            projects.map(p => (
            <tr key={p.id}>
              <td>{p.name}</td>
              <td>{p.chain}</td>
              <td>{p.funding}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <a href="/export/csv">Export CSV</a>
    </div>
  );
}