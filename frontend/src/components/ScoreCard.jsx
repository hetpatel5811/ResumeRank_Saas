function ScoreCard({ title, score, description }) {
  const safeScore = Math.min(Math.max(Number(score) || 0, 0), 100);

  return (
    <div className="score-card">
      <div className="score-card-top">
        <h3>{title}</h3>
        <span>{safeScore}%</span>
      </div>

      <div className="score-bar">
        <div style={{ width: `${safeScore}%` }}></div>
      </div>

      <p>{description}</p>
    </div>
  );
}

export default ScoreCard;
