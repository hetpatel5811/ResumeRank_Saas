import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, ArrowRight, BriefcaseBusiness } from "lucide-react";
import api from "../api/api";

function Register() {
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

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/api/auth/register", form);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
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
          <BriefcaseBusiness size={24} />
        </div>

        <h1>Create Account</h1>
        <p className="auth-subtitle">
          Start analyzing resumes with intelligent job matching.
        </p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleRegister}>
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
            {loading ? "Creating..." : "Create Account"}
            <ArrowRight size={20} />
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;
