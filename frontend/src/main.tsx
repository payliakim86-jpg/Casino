import { createRoot } from "react-dom/client";
import "@fontsource/cormorant-garamond/600.css";
import "@fontsource/cormorant-garamond/700.css";
import "@fontsource-variable/manrope";
import App from "./App";
import "./styles.css";

createRoot(document.getElementById("root")!).render(<App />);
