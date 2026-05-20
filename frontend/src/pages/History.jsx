import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Download, Eye, Trash2 } from "lucide-react";
import Navbar from "../components/Navbar";
import api from "../api/api";

const SCORE_FILTERS = [
  { value: "all", label: "all scores" },
  { value: "80_plus", label: "80+ strong match" },
  { value: "60_79", label: "60-79 medium match" },
  { value: "under_60", label: "under 60 low match" },
  { value: "unknown", label: "no score" },
];

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [scoreFilter, setScoreFilter] = useState("all");
  const [sortBy, setSortBy] = useState("newest");

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

  const statusOptions = useMemo(() => {
    const values = new Set(history.map((item) => item.status).filter(Boolean));
    return ["all", ...Array.from(values)];
  }, [history]);

  const filteredHistory = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    const filtered = history.filter((item) => {
      const score = item.overall_score;
      const hasScore = typeof score === "number";

      const matchesSearch =
        !normalizedSearch || item.resume_filename.toLowerCase().includes(normalizedSearch);

      const matchesStatus = statusFilter === "all" || item.status === statusFilter;

      const matchesScore =
        scoreFilter === "all" ||
        (scoreFilter === "80_plus" && hasScore && score >= 80) ||
        (scoreFilter === "60_79" && hasScore && score >= 60 && score < 80) ||
        (scoreFilter === "under_60" && hasScore && score < 60) ||
        (scoreFilter === "unknown" && !hasScore);

      return matchesSearch && matchesStatus && matchesScore;
    });

    return filtered.sort((a, b) => {
      if (sortBy === "oldest") {
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      }
      if (sortBy === "score_high") {
        return (b.overall_score ?? -1) - (a.overall_score ?? -1);
      }
      if (sortBy === "score_low") {
        return (a.overall_score ?? 101) - (b.overall_score ?? 101);
      }
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
  }, [history, search, statusFilter, scoreFilter, sortBy]);

  const averageScore = useMemo(() => {
    const scores = filteredHistory
      .map((item) => item.overall_score)
      .filter((score) => typeof score === "number");

    if (scores.length === 0) return null;

    const avg = scores.reduce((sum, value) => sum + value, 0) / scores.length;
    return Math.round(avg);
  }, [filteredHistory]);

  const exportCsv = () => {
    const headers = ["resume_filename", "status", "overall_score", "created_at", "scan_id"];

    const rows = filteredHistory.map((item) => [
      item.resume_filename,
      item.status,
      item.overall_score ?? "",
      new Date(item.created_at).toISOString(),
      item.scan_id,
    ]);

    const csv = [headers, ...rows]
      .map((row) =>
        row
          .map((cell) => `"${String(cell ?? "").replace(/"/g, '""')}"`)
          .join(",")
      )
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `resume-rank-history-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

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

        <section className="history-controls-card">
          <input
            type="text"
            placeholder="Search resume filename..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            {statusOptions.map((option) => (
              <option value={option} key={option}>
                {option}
              </option>
            ))}
          </select>

          <select value={scoreFilter} onChange={(event) => setScoreFilter(event.target.value)}>
            {SCORE_FILTERS.map((option) => (
              <option value={option.value} key={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <select value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
            <option value="newest">newest first</option>
            <option value="oldest">oldest first</option>
            <option value="score_high">score high to low</option>
            <option value="score_low">score low to high</option>
          </select>

          <button className="secondary-link history-export-btn" onClick={exportCsv} type="button">
            <Download size={16} />
            Export CSV
          </button>
        </section>

        <section className="history-insight-row">
          <div className="jobs-summary-card">
            <h3>{filteredHistory.length}</h3>
            <p>Visible Scans</p>
          </div>
          <div className="jobs-summary-card">
            <h3>{averageScore === null ? "--" : `${averageScore}%`}</h3>
            <p>Average Score</p>
          </div>
        </section>

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
                {filteredHistory.map((item) => (
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

                {filteredHistory.length === 0 && (
                  <tr>
                    <td colSpan={5}>
                      <p className="empty-text">No scans match your current filters.</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default History;
