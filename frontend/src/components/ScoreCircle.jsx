function ScoreCircle({ score = 0, label = "Overall Match" }) {
  const safeScore = Math.min(Math.max(Number(score) || 0, 0), 100);

  const color =
    safeScore >= 80
      ? "#0f9f6f"
      : safeScore >= 60
      ? "#0f6ef4"
      : safeScore >= 40
      ? "#d97706"
      : "#dc2626";

  return (
    <div className="score-circle-card">
      <div
        className="score-circle"
        style={{
          background: `conic-gradient(${color} ${safeScore * 3.6}deg, #e2e8f3 0deg)`,
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
