import React from "react";
import { createRoot } from "react-dom/client";
import LoginPage from "./LoginPage";

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<LoginPage />);
