import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  BriefcaseBusiness,
  LayoutDashboard,
  FileSearch,
  History,
  CreditCard,
  LogOut,
} from "lucide-react";

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();

  const pathname = location.pathname;

  const isDashboard = pathname.startsWith("/dashboard");
  const isAnalyze = pathname.startsWith("/analyze");
  const isHistory = pathname.startsWith("/history") || pathname.startsWith("/result");
  const isBilling = pathname.startsWith("/billing");

  const logout = () => {
    localStorage.removeItem("resume_rank_token");
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <BriefcaseBusiness size={22} />
        </div>
        <div>
          <h2>ResumeRank</h2>
          <p>Resume Intelligence</p>
        </div>
      </div>

      <nav className="nav-links">
        <Link className={isDashboard ? "active" : ""} to="/dashboard">
          <LayoutDashboard size={20} />
          Dashboard
        </Link>

        <Link className={isAnalyze ? "active" : ""} to="/analyze">
          <FileSearch size={20} />
          Analyze Resume
        </Link>

        <Link className={isHistory ? "active" : ""} to="/history">
          <History size={20} />
          History
        </Link>

        <Link className={isBilling ? "active" : ""} to="/billing">
          <CreditCard size={20} />
          Billing
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
