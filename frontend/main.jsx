import React from "react";
import { createRoot } from "react-dom/client";
import LoginPage from "./LoginPage";
import App from "./app/App";

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<LoginPage />);
