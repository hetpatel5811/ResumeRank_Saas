import { useState } from "react";
import Navbar from "../components/Navbar";
import api from "../api/api";

function CareerTools() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [coverLetterForm, setCoverLetterForm] = useState({
    target_role: "",
    company_name: "",
    job_description: "",
    resume_points: "",
    tone: "professional",
  });
  const [coverLetterResult, setCoverLetterResult] = useState(null);

  const [linkedinForm, setLinkedinForm] = useState({
    linkedin_text: "",
    job_description: "",
  });
  const [linkedinResult, setLinkedinResult] = useState(null);

  const [interviewForm, setInterviewForm] = useState({
    target_role: "",
    job_description: "",
    experience_level: "mid",
  });
  const [interviewResult, setInterviewResult] = useState(null);

  const [bulletForm, setBulletForm] = useState({
    bullet_points: "",
    job_description: "",
  });
  const [bulletResult, setBulletResult] = useState(null);

  const callTool = async (request) => {
    setLoading(true);
    setError("");
    try {
      await request();
    } catch (err) {
      setError(err.response?.data?.detail || "Tool request failed.");
    } finally {
      setLoading(false);
    }
  };

  const generateCoverLetter = (event) => {
    event.preventDefault();
    callTool(async () => {
      const res = await api.post("/api/tools/cover-letter", {
        ...coverLetterForm,
        resume_points: coverLetterForm.resume_points
          .split("\n")
          .map((item) => item.trim())
          .filter(Boolean),
      });
      setCoverLetterResult(res.data);
    });
  };

  const optimizeLinkedin = (event) => {
    event.preventDefault();
    callTool(async () => {
      const res = await api.post("/api/tools/linkedin-optimize", linkedinForm);
      setLinkedinResult(res.data);
    });
  };

  const generateInterviewQuestions = (event) => {
    event.preventDefault();
    callTool(async () => {
      const res = await api.post("/api/tools/interview-practice", interviewForm);
      setInterviewResult(res.data);
    });
  };

  const optimizeBullets = (event) => {
    event.preventDefault();
    callTool(async () => {
      const bullets = bulletForm.bullet_points
        .split("\n")
        .map((item) => item.trim())
        .filter(Boolean);
      const res = await api.post("/api/tools/optimize-bullets", {
        bullet_points: bullets,
        job_description: bulletForm.job_description,
      });
      setBulletResult(res.data);
    });
  };

  return (
    <div className="app-shell">
      <Navbar />

      <main className="main-content">
        <div className="page-heading">
          <span className="eyebrow">AI Assist</span>
          <h1>Career Tools</h1>
          <p>Generate cover letters, improve LinkedIn, practice interviews, and optimize bullets.</p>
        </div>

        {error && <div className="error-box">{error}</div>}

        <section className="tools-grid">
          <article className="tool-card">
            <h2>Cover Letter Generator</h2>
            <form onSubmit={generateCoverLetter} className="tool-form">
              <input
                placeholder="Target Role"
                value={coverLetterForm.target_role}
                onChange={(e) => setCoverLetterForm((prev) => ({ ...prev, target_role: e.target.value }))}
                required
              />
              <input
                placeholder="Company Name"
                value={coverLetterForm.company_name}
                onChange={(e) => setCoverLetterForm((prev) => ({ ...prev, company_name: e.target.value }))}
                required
              />
              <select
                value={coverLetterForm.tone}
                onChange={(e) => setCoverLetterForm((prev) => ({ ...prev, tone: e.target.value }))}
              >
                <option value="professional">professional</option>
                <option value="confident">confident</option>
                <option value="concise">concise</option>
              </select>
              <textarea
                placeholder="Job Description"
                value={coverLetterForm.job_description}
                onChange={(e) => setCoverLetterForm((prev) => ({ ...prev, job_description: e.target.value }))}
                required
              />
              <textarea
                placeholder="Resume Highlights (one per line)"
                value={coverLetterForm.resume_points}
                onChange={(e) => setCoverLetterForm((prev) => ({ ...prev, resume_points: e.target.value }))}
              />
              <button className="primary-btn" disabled={loading}>
                {loading ? "Generating..." : "Generate Cover Letter"}
              </button>
            </form>
            {coverLetterResult && (
              <div className="tool-result">
                <pre>{coverLetterResult.cover_letter}</pre>
              </div>
            )}
          </article>

          <article className="tool-card">
            <h2>LinkedIn Optimizer</h2>
            <form onSubmit={optimizeLinkedin} className="tool-form">
              <textarea
                placeholder="Paste LinkedIn About/Headline text"
                value={linkedinForm.linkedin_text}
                onChange={(e) => setLinkedinForm((prev) => ({ ...prev, linkedin_text: e.target.value }))}
                required
              />
              <textarea
                placeholder="Paste Job Description"
                value={linkedinForm.job_description}
                onChange={(e) => setLinkedinForm((prev) => ({ ...prev, job_description: e.target.value }))}
                required
              />
              <button className="primary-btn" disabled={loading}>
                {loading ? "Analyzing..." : "Optimize LinkedIn"}
              </button>
            </form>
            {linkedinResult && (
              <div className="tool-result">
                <p><strong>Headline:</strong> {linkedinResult.optimized_headline}</p>
                <p><strong>Missing Keywords:</strong> {linkedinResult.missing_keywords.join(", ") || "None"}</p>
              </div>
            )}
          </article>

          <article className="tool-card">
            <h2>Interview Practice</h2>
            <form onSubmit={generateInterviewQuestions} className="tool-form">
              <input
                placeholder="Target Role"
                value={interviewForm.target_role}
                onChange={(e) => setInterviewForm((prev) => ({ ...prev, target_role: e.target.value }))}
                required
              />
              <select
                value={interviewForm.experience_level}
                onChange={(e) => setInterviewForm((prev) => ({ ...prev, experience_level: e.target.value }))}
              >
                <option value="fresher">fresher</option>
                <option value="mid">mid</option>
                <option value="senior">senior</option>
              </select>
              <textarea
                placeholder="Job Description"
                value={interviewForm.job_description}
                onChange={(e) => setInterviewForm((prev) => ({ ...prev, job_description: e.target.value }))}
                required
              />
              <button className="primary-btn" disabled={loading}>
                {loading ? "Generating..." : "Create Interview Set"}
              </button>
            </form>
            {interviewResult && (
              <div className="tool-result">
                <ul>
                  {interviewResult.questions.map((item, index) => (
                    <li key={`${item.category}-${index}`}>
                      <strong>{item.category}:</strong> {item.question}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </article>

          <article className="tool-card">
            <h2>Bullet Optimizer</h2>
            <form onSubmit={optimizeBullets} className="tool-form">
              <textarea
                placeholder="Paste resume bullets (one per line)"
                value={bulletForm.bullet_points}
                onChange={(e) => setBulletForm((prev) => ({ ...prev, bullet_points: e.target.value }))}
                required
              />
              <textarea
                placeholder="Job Description"
                value={bulletForm.job_description}
                onChange={(e) => setBulletForm((prev) => ({ ...prev, job_description: e.target.value }))}
                required
              />
              <button className="primary-btn" disabled={loading}>
                {loading ? "Optimizing..." : "Optimize Bullets"}
              </button>
            </form>
            {bulletResult && (
              <div className="tool-result">
                {bulletResult.optimized_bullets.map((item, index) => (
                  <div key={`${item.original}-${index}`} className="tool-bullet-item">
                    <p><strong>Original:</strong> {item.original}</p>
                    <p><strong>Optimized:</strong> {item.optimized}</p>
                  </div>
                ))}
              </div>
            )}
          </article>
        </section>
      </main>
    </div>
  );
}

export default CareerTools;
