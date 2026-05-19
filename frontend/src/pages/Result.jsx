import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import api from "../api/api";
import ScoreCircle from "../components/ScoreCircle";
import ScoreCard from "../components/ScoreCard";
import BadgeList from "../components/BadgeList";
import SuggestionCard from "../components/SuggestionCard";

function Result() {
  const { scanId } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchResult = async () => {
    try {
      const res = await api.get(`/api/scans/${scanId}`);
      setResult(res.data);
    } catch (err) {
      console.log(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResult();
  }, [scanId]);

  if (loading) {
    return (
      <div className="app-shell">
        <Navbar />
        <main className="main-content">
          <div className="loading-box">Loading result...</div>
        </main>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="app-shell">
        <Navbar />
        <main className="main-content">
          <div className="empty-panel">
            <h2>Result not found</h2>
            <Link to="/history" className="primary-link">
              Back to History
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Navbar />

      <main className="main-content">
        <div className="result-header">
          <div>
            <span className="eyebrow">Scan Result</span>
            <h1>{result.resume_filename}</h1>
            <p>{new Date(result.created_at).toLocaleString()}</p>
          </div>

          <Link to="/analyze" className="primary-link">
            New Scan
          </Link>
        </div>

        <section className="result-score-grid">
          <ScoreCircle score={result.overall_score} />

          <div className="subscore-grid">
            <ScoreCard
              title="Keyword Match"
              score={result.keyword_score}
              description="TF-IDF similarity between job description and resume."
            />

            <ScoreCard
              title="Skills Match"
              score={result.skills_score}
              description="Intersection of JD skills and resume skills."
            />

            <ScoreCard
              title="Experience"
              score={result.experience_score}
              description="Experience years detected from resume."
            />

            <ScoreCard
              title="Format"
              score={result.format_score}
              description="ATS-friendly resume structure and sections."
            />
          </div>
        </section>

        <section className="result-two-col">
          <BadgeList
            title="Matched Skills"
            items={result.matched_skills}
            type="success"
          />

          <BadgeList
            title="Missing Skills"
            items={result.missing_skills}
            type="danger"
          />
        </section>

        <section className="result-two-col">
          <BadgeList
            title="Matched Keywords"
            items={result.matched_keywords}
            type="success"
          />

          <BadgeList
            title="Missing Keywords"
            items={result.missing_keywords}
            type="warning"
          />
        </section>

        <section className="suggestions-section">
          <h2>Improvement Suggestions</h2>

          <div className="suggestion-list">
            {result.suggestions.map((suggestion, index) => (
              <SuggestionCard
                suggestion={suggestion}
                key={suggestion.id || `${suggestion.category}-${index}`}
              />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default Result;
