import { useEffect, useState } from "react";
import { ExternalLink, Trash2 } from "lucide-react";
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
  follow_up_at: "",
};

const STATUS_OPTIONS = [
  "saved",
  "applied",
  "screening",
  "interview",
  "offer",
  "rejected",
];

const FOLLOW_UP_URGENCY_OPTIONS = ["all", "overdue", "due_soon", "upcoming", "none"];

const DAY_MS = 24 * 60 * 60 * 1000;

function getFollowUpUrgency(followUpAt) {
  if (!followUpAt) return "none";

  const dueTime = new Date(followUpAt).getTime();
  if (Number.isNaN(dueTime)) return "none";

  const now = Date.now();
  if (dueTime < now) return "overdue";

  const diff = dueTime - now;
  if (diff <= 2 * DAY_MS) return "due_soon";

  return "upcoming";
}

function JobTracker() {
  const [jobs, setJobs] = useState([]);
  const [summary, setSummary] = useState({
    total: 0,
    by_status: {},
    overdue_follow_ups: 0,
    due_next_7_days: 0,
  });
  const [form, setForm] = useState(INITIAL_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [urgencyFilter, setUrgencyFilter] = useState("all");

  const fetchData = async () => {
    try {
      const [jobsRes, summaryRes] = await Promise.all([
        api.get("/api/jobs"),
        api.get("/api/jobs/summary"),
      ]);

      setJobs(jobsRes.data || []);
      setSummary(
        summaryRes.data || {
          total: 0,
          by_status: {},
          overdue_follow_ups: 0,
          due_next_7_days: 0,
        }
      );
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

    const followUpIso = form.follow_up_at ? new Date(form.follow_up_at).toISOString() : null;

    try {
      await api.post("/api/jobs", {
        ...form,
        follow_up_at: followUpIso,
      });
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

  const clearFollowUp = async (jobId) => {
    try {
      await api.patch(`/api/jobs/${jobId}`, { follow_up_at: null });
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to clear follow-up reminder.");
    }
  };

  const normalizedSearch = search.trim().toLowerCase();

  const filteredJobs = jobs.filter((job) => {
    const urgency = getFollowUpUrgency(job.follow_up_at);

    const matchesSearch =
      !normalizedSearch ||
      [job.company, job.role, job.location, job.salary_text, job.notes]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(normalizedSearch));

    const matchesStatus = statusFilter === "all" || job.status === statusFilter;
    const matchesUrgency = urgencyFilter === "all" || urgency === urgencyFilter;

    return matchesSearch && matchesStatus && matchesUrgency;
  });

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
          <div className="jobs-summary-card">
            <h3>{summary.overdue_follow_ups || 0}</h3>
            <p>Overdue Follow-ups</p>
          </div>
          <div className="jobs-summary-card">
            <h3>{summary.due_next_7_days || 0}</h3>
            <p>Due In 7 Days</p>
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
            <input
              type="datetime-local"
              name="follow_up_at"
              value={form.follow_up_at}
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

        <section className="jobs-filters-card">
          <input
            type="text"
            placeholder="Search by company, role, location, notes..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="all">all statuses</option>
            {STATUS_OPTIONS.map((statusValue) => (
              <option value={statusValue} key={statusValue}>
                {statusValue}
              </option>
            ))}
          </select>

          <select value={urgencyFilter} onChange={(event) => setUrgencyFilter(event.target.value)}>
            {FOLLOW_UP_URGENCY_OPTIONS.map((value) => (
              <option key={value} value={value}>
                {value.replace("_", " ")}
              </option>
            ))}
          </select>
        </section>

        {loading ? (
          <div className="loading-box">Loading job tracker...</div>
        ) : filteredJobs.length === 0 ? (
          <div className="empty-panel">
            <h3>No jobs match these filters</h3>
            <p>Try changing search or filter values, or add a new job.</p>
          </div>
        ) : (
          <section className="jobs-list">
            {filteredJobs.map((job) => {
              const urgency = getFollowUpUrgency(job.follow_up_at);

              return (
                <article className="job-item" key={job.id}>
                <div>
                  <h3>{job.role}</h3>
                  <p>{job.company}</p>
                  {job.location && <small>{job.location}</small>}
                  <div className="job-item-meta">
                    {job.salary_text && <span className="job-chip">{job.salary_text}</span>}
                    {job.follow_up_at && (
                      <span className={`job-chip urgency-${urgency}`}>
                        Follow-up: {new Date(job.follow_up_at).toLocaleString()}
                      </span>
                    )}
                    {job.job_url && (
                      <a href={job.job_url} target="_blank" rel="noreferrer" className="job-chip link-chip">
                        Open Job <ExternalLink size={14} />
                      </a>
                    )}
                  </div>
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

                  {job.follow_up_at && (
                    <button
                      className="secondary-link compact-btn"
                      type="button"
                      onClick={() => clearFollowUp(job.id)}
                    >
                      Clear Follow-up
                    </button>
                  )}

                  <button
                    className="icon-btn danger"
                    onClick={() => deleteJob(job.id)}
                    type="button"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </article>
              );
            })}
          </section>
        )}
      </main>
    </div>
  );
}

export default JobTracker;
