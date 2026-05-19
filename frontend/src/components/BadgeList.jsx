function BadgeList({ title, items = [], type = "success" }) {
  return (
    <div className="badge-box">
      <h3>{title}</h3>

      {items.length === 0 ? (
        <p className="empty-text">No items found</p>
      ) : (
        <div className="badge-list">
          {items.map((item, index) => (
            <span key={index} className={`badge ${type}`}>
              {item}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default BadgeList;