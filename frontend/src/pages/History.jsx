import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Trash2, Eye } from "lucide-react";
import Navbar from "../components/Navbar";
import api from "../api/api";

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    try {
      const res = await api.get("/api/scans/history");
      setHistory(res.data);
    } catch (err) {
      console.log(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteScan = async (scanId) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this scan?");

    if (!confirmDelete) return;

    try {
      await api.delete(`/api/scans/${scanId}`);
      setHistory(history.filter((item) => item.scan_id !== scanId));
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete scan");
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="app-shell">
      <Navbar />

      <main className="main-content">
        <div className="result-header">
          <div>
            <span className="eyebrow">Saved Scans</span>
            <h1>Scan History</h1>
            <p>View previous resume analysis results.</p>
          </div>

          <Link to="/analyze" className="primary-link">
            New Scan
          </Link>
        </div>

        {loading ? (
          <div className="loading-box">Loading history...</div>
        ) : history.length === 0 ? (
          <div className="empty-panel">
            <h2>No scan history found</h2>
            <p>Analyze your first resume to see results here.</p>
            <Link to="/analyze" className="primary-link">
              Analyze Resume
            </Link>
          </div>
        ) : (
          <div className="history-table-card">
            <table>
              <thead>
                <tr>
                  <th>Resume</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item) => (
                  <tr key={item.scan_id}>
                    <td>{item.resume_filename}</td>
                    <td>
                      <span className="status-pill">{item.status}</span>
                    </td>
                    <td>
                      <strong>
                        {typeof item.overall_score === "number" ? `${item.overall_score}%` : "--"}
                      </strong>
                    </td>
                    <td>{new Date(item.created_at).toLocaleString()}</td>
                    <td>
                      <div className="table-actions">
                        <Link to={`/result/${item.scan_id}`} className="icon-btn">
                          <Eye size={18} />
                        </Link>

                        <button
                          className="icon-btn danger"
                          onClick={() => deleteScan(item.scan_id)}
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default History;
