import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import Navbar from "../components/Navbar";
import api from "../api/api";

const INITIAL_FORM = {
  company: "",
  role: "",
  status: "saved",
  job_url: "",
  location: "",
  salary_text: "",
  notes: "",
};

const STATUS_OPTIONS = [
  "saved",
  "applied",
  "screening",
  "interview",
  "offer",
  "rejected",
];

function JobTracker() {
  const [jobs, setJobs] = useState([]);
  const [summary, setSummary] = useState({ total: 0, by_status: {} });
  const [form, setForm] = useState(INITIAL_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const fetchData = async () => {
    try {
      const [jobsRes, summaryRes] = await Promise.all([
        api.get("/api/jobs"),
        api.get("/api/jobs/summary"),
      ]);

      setJobs(jobsRes.data || []);
      setSummary(summaryRes.data || { total: 0, by_status: {} });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load job tracker data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => {
      fetchData();
    }, 0);

    return () => window.clearTimeout(timer);
  }, []);

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const createJob = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      await api.post("/api/jobs", form);
      setForm(INITIAL_FORM);
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create job application.");
    } finally {
      setSaving(false);
    }
  };

  const updateStatus = async (jobId, statusValue) => {
    try {
      await api.patch(`/api/jobs/${jobId}`, { status: statusValue });
      setJobs((prev) =>
        prev.map((job) => (job.id === jobId ? { ...job, status: statusValue } : job))
      );
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update status.");
    }
  };

  const deleteJob = async (jobId) => {
    const confirmed = window.confirm("Delete this tracked job?");
    if (!confirmed) return;

    try {
      await api.delete(`/api/jobs/${jobId}`);
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete job.");
    }
  };

  return (
    <div className="app-shell">
      <Navbar />

      <main className="main-content">
        <div className="page-heading">
          <span className="eyebrow">Pipeline</span>
          <h1>Job Tracker</h1>
          <p>Track every opportunity from saved jobs to final offers.</p>
        </div>

        <section className="jobs-summary-grid">
          <div className="jobs-summary-card">
            <h3>{summary.total || 0}</h3>
            <p>Total Tracked</p>
          </div>
          {STATUS_OPTIONS.map((statusValue) => (
            <div className="jobs-summary-card" key={statusValue}>
              <h3>{summary.by_status?.[statusValue] || 0}</h3>
              <p>{statusValue}</p>
            </div>
          ))}
        </section>

        <section className="jobs-form-card">
          <h2>Add Job</h2>
          <form className="jobs-form-grid" onSubmit={createJob}>
            <input
              type="text"
              name="company"
              placeholder="Company"
              value={form.company}
              onChange={handleFormChange}
              required
            />
            <input
              type="text"
              name="role"
              placeholder="Role"
              value={form.role}
              onChange={handleFormChange}
              required
            />
            <select name="status" value={form.status} onChange={handleFormChange}>
              {STATUS_OPTIONS.map((statusValue) => (
                <option value={statusValue} key={statusValue}>
                  {statusValue}
                </option>
              ))}
            </select>
            <input
              type="url"
              name="job_url"
              placeholder="Job URL"
              value={form.job_url}
              onChange={handleFormChange}
            />
            <input
              type="text"
              name="location"
              placeholder="Location"
              value={form.location}
              onChange={handleFormChange}
            />
            <input
              type="text"
              name="salary_text"
              placeholder="Salary (optional)"
              value={form.salary_text}
              onChange={handleFormChange}
            />
            <textarea
              name="notes"
              placeholder="Notes / follow-up context"
              value={form.notes}
              onChange={handleFormChange}
            />
            <button className="primary-btn" disabled={saving}>
              {saving ? "Saving..." : "Add to Tracker"}
            </button>
          </form>
        </section>

        {error && <div className="error-box">{error}</div>}

        {loading ? (
          <div className="loading-box">Loading job tracker...</div>
        ) : jobs.length === 0 ? (
          <div className="empty-panel">
            <h3>No tracked jobs yet</h3>
            <p>Add your first application to start managing your pipeline.</p>
          </div>
        ) : (
          <section className="jobs-list">
            {jobs.map((job) => (
              <article className="job-item" key={job.id}>
                <div>
                  <h3>{job.role}</h3>
                  <p>{job.company}</p>
                  {job.location && <small>{job.location}</small>}
                </div>

                <div className="job-item-actions">
                  <select
                    value={job.status}
                    onChange={(e) => updateStatus(job.id, e.target.value)}
                  >
                    {STATUS_OPTIONS.map((statusValue) => (
                      <option key={statusValue} value={statusValue}>
                        {statusValue}
                      </option>
                    ))}
                  </select>

                  <button
                    className="icon-btn danger"
                    onClick={() => deleteJob(job.id)}
                    type="button"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </article>
            ))}
          </section>
        )}
      </main>
    </div>
  );
}

export default JobTracker;
