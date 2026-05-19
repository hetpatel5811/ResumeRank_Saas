import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  FileSearch,
  History,
  LogOut,
  Sparkles,
} from "lucide-react";

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => location.pathname === path;

  const logout = () => {
    localStorage.removeItem("resume_rank_token");
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <Sparkles size={24} />
        </div>
        <div>
          <h2>ResumeRank</h2>
          <p>AI Resume Match</p>
        </div>
      </div>

      <nav className="nav-links">
        <Link className={isActive("/dashboard") ? "active" : ""} to="/dashboard">
          <LayoutDashboard size={20} />
          Dashboard
        </Link>

        <Link className={isActive("/analyze") ? "active" : ""} to="/analyze">
          <FileSearch size={20} />
          Analyze Resume
        </Link>

        <Link className={isActive("/history") ? "active" : ""} to="/history">
          <History size={20} />
          History
        </Link>
      </nav>

      <button className="logout-btn" onClick={logout}>
        <LogOut size={20} />
        Logout
      </button>
    </aside>
  );
}

export default Navbar;