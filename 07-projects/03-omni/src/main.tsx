import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { IconRegistryProvider } from "@/core/icons";
import { ThemeProvider } from "@/core/theme/ThemeProvider";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <IconRegistryProvider>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </IconRegistryProvider>
  </React.StrictMode>
);
