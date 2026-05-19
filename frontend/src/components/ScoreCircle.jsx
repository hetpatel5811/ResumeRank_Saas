function ScoreCircle({ score = 0, label = "Overall Match" }) {
  const safeScore = Math.min(Math.max(score, 0), 100);

  return (
    <div className="score-circle-card">
      <div
        className="score-circle"
        style={{
          background: `conic-gradient(#10b981 ${safeScore * 3.6}deg, #e5e7eb 0deg)`,
        }}
      >
        <div className="score-inner">
          <h1>{safeScore}</h1>
          <span>/100</span>
        </div>
      </div>
      <p>{label}</p>
    </div>
  );
}

export default ScoreCircle;