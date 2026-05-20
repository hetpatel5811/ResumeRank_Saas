import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";

import "./styles/global.css";
import "./styles/auth.css";
import "./styles/layout.css";
import "./styles/dashboard.css";
import "./styles/analyze.css";
import "./styles/result.css";
import "./styles/billing.css";
import "./styles/jobs.css";
import "./styles/career-tools.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
