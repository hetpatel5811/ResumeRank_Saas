function ScoreCard({ title, score, description }) {
  return (
    <div className="score-card">
      <div className="score-card-top">
        <h3>{title}</h3>
        <span>{score}%</span>
      </div>

      <div className="score-bar">
        <div style={{ width: `${score}%` }}></div>
      </div>

      <p>{description}</p>
    </div>
  );
}

export default ScoreCard;