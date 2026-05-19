import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadCloud, FileText, ShieldCheck } from "lucide-react";
import Navbar from "../components/Navbar";
import api from "../api/api";

function Analyze() {
  const navigate = useNavigate();

  const [jobDescription, setJobDescription] = useState("");
  const [resume, setResume] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (e) => {
    e.preventDefault();

    if (!resume) {
      setError("Please upload your resume file.");
      return;
    }

    setError("");
    setLoading(true);

    const formData = new FormData();
    formData.append("job_description", jobDescription);
    formData.append("resume", resume);

    try {
      const res = await api.post("/api/scans/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      navigate(`/result/${res.data.scan_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Resume analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <Navbar />

      <main className="main-content">
        <div className="page-heading">
          <span className="eyebrow">New Scan</span>
          <h1>Analyze Resume</h1>
          <p>Paste a job description and upload your resume to get a match score.</p>
        </div>

        <form className="analyze-grid" onSubmit={handleAnalyze}>
          <div className="jd-panel">
            <div className="panel-title">
              <FileText size={22} />
              <h2>Job Description</h2>
            </div>

            <textarea
              placeholder="Paste job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              required
            ></textarea>
          </div>

          <div className="upload-panel">
            <div className="upload-card">
              <div className="upload-icon">
                <UploadCloud size={42} />
              </div>

              <h2>Upload Resume</h2>
              <p>Supported formats: PDF, DOCX</p>

              <label className="file-input-label">
                Choose File
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(e) => setResume(e.target.files[0])}
                />
              </label>

              {resume && <div className="selected-file">{resume.name}</div>}
            </div>

            <div className="scan-info-card">
              <ShieldCheck size={24} />
              <p>
                Your resume will be scored using TF-IDF keyword similarity,
                skills matching, experience detection, and ATS format checks.
              </p>
            </div>

            {error && <div className="error-box">{error}</div>}

            <button className="analyze-btn" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Resume"}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}

export default Analyze;
