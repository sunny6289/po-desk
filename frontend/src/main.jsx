import React from "react";
import ReactDOM from "react-dom/client";
import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import App from "./App.jsx";
import Requests from "./Requests.jsx";

import "./index.css";

ReactDOM.createRoot(
  document.getElementById("root")
).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>

        {/* Home */}
        <Route
          path="/"
          element={<App />}
        />

        {/* Previous Requests */}
        <Route
          path="/requests"
          element={<Requests />}
        />

      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);