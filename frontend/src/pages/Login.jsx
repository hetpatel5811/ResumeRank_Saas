import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, ArrowRight, Sparkles } from "lucide-react";
import api from "../api/api";

function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api.post("/api/auth/login", form);

      localStorage.setItem("resume_rank_token", res.data.access_token);

      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg-orb orb-one"></div>
      <div className="auth-bg-orb orb-two"></div>

      <div className="auth-card">
        <div className="auth-logo">
          <Sparkles size={28} />
        </div>

        <h1>Welcome Back</h1>
        <p className="auth-subtitle">
          Login to analyze your resume and improve your job match score.
        </p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleLogin}>
          <div className="input-group">
            <Mail size={20} />
            <input
              type="email"
              name="email"
              placeholder="Email address"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="input-group">
            <Lock size={20} />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={form.password}
              onChange={handleChange}
              required
            />
          </div>

          <button className="primary-btn" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
            <ArrowRight size={20} />
          </button>
        </form>

        <p className="auth-footer">
          New to ResumeRank? <Link to="/register">Create account</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;