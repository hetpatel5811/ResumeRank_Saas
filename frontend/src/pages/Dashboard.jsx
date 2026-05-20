import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FileSearch, History, TrendingUp, Gauge, Sparkles } from "lucide-react";
import Navbar from "../components/Navbar";
import api from "../api/api";

function Dashboard() {
  const [user, setUser] = useState(null);
  const [history, setHistory] = useState([]);

  const fetchData = async () => {
    try {
      const userRes = await api.get("/api/auth/me");
      const historyRes = await api.get("/api/scans/history");

      setUser(userRes.data);
      setHistory(historyRes.data);
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const latestScore = history.length > 0 ? history[0].overall_score : null;
  const userPlan = (user?.plan || "free").toUpperCase();

  return (
    <div className="app-shell">
      <Navbar />

      <main className="main-content">
        <section className="hero-section">
          <div>
            <span className="eyebrow">Resume Intelligence Platform</span>
            <h1>Improve your resume match score before applying.</h1>
            <p>
              Upload your resume, paste a job description, and get a complete
              scoring breakdown with actionable suggestions.
            </p>

            <div className="hero-actions">
              <Link to="/analyze" className="primary-link">
                Analyze Resume
              </Link>
              <Link to="/history" className="secondary-link">
                View History
              </Link>
              {userPlan === "FREE" && (
                <Link to="/billing" className="secondary-link">
                  Upgrade Plan
                </Link>
              )}
            </div>
          </div>

          <div className="hero-glass-card">
            <Gauge size={34} />
            <h2>{typeof latestScore === "number" ? latestScore : "--"}</h2>
            <p>Latest Match Score</p>
          </div>
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <FileSearch />
            <div>
              <h3>{user?.scan_count || 0}</h3>
              <p>Total Scans</p>
            </div>
          </div>

          <div className="stat-card">
            <TrendingUp />
            <div>
              <h3>{typeof latestScore === "number" ? `${latestScore}%` : "--"}</h3>
              <p>Latest Score</p>
            </div>
          </div>

          <div className="stat-card">
            <History />
            <div>
              <h3>{history.length}</h3>
              <p>Saved Results</p>
            </div>
          </div>

          <div className="stat-card">
            <Sparkles />
            <div>
              <h3>{userPlan}</h3>
              <p>Current Plan</p>
            </div>
          </div>
        </section>

        <section className="recent-section">
          <div className="section-header">
            <h2>Recent Scans</h2>
            <Link to="/history">See all</Link>
          </div>

          {history.length === 0 ? (
            <div className="empty-panel">
              <h3>No scans yet</h3>
              <p>Start by analyzing your first resume.</p>
              <Link to="/analyze" className="primary-link">
                Analyze Now
              </Link>
            </div>
          ) : (
            <div className="recent-list">
              {history.slice(0, 4).map((item) => (
                <Link
                  to={`/result/${item.scan_id}`}
                  className="recent-item"
                  key={item.scan_id}
                >
                  <div>
                    <h3>{item.resume_filename}</h3>
                    <p>{new Date(item.created_at).toLocaleString()}</p>
                  </div>
                  <span>{typeof item.overall_score === "number" ? `${item.overall_score}%` : "--"}</span>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default Dashboard;
