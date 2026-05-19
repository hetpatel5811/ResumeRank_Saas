import { AlertCircle, CheckCircle, Info } from "lucide-react";

function SuggestionCard({ suggestion }) {
  const icon =
    suggestion.priority === "high" ? (
      <AlertCircle size={20} />
    ) : suggestion.priority === "medium" ? (
      <Info size={20} />
    ) : (
      <CheckCircle size={20} />
    );

  return (
    <div className={`suggestion-card ${suggestion.priority}`}>
      <div className="suggestion-icon">{icon}</div>

      <div>
        <div className="suggestion-meta">
          <span>{suggestion.category}</span>
          <small>{suggestion.priority}</small>
        </div>
        <p>{suggestion.suggestion_text}</p>
      </div>
    </div>
  );
}

export default SuggestionCard;
