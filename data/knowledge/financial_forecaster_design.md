Financial Forecaster App - Design Standards & Golden Prompt
1. Purpose
This document defines the strict design and functional requirements for the "Financial Modeling Suite" HTML application. Use this standard when generating new dashboards for different companies to ensure UI/UX consistency.

2. The "Golden Prompt"

Copy and paste this prompt when starting a new financial modeling task:
"Act as an expert Financial Analyst and Web Developer. I need you to build a Single-File HTML Financial Dashboard for [INSERT TICKER/COMPANY NAME].
Crucial Requirement: You must use the specific design patterns, CSS styling, and JavaScript logic defined in the 'Standard Template' I have uploaded/pasted below.

Design Specs (Non-Negotiable):
Theme: Dark Mode only. Background: #0f172a (Slate-900). Cards: Glassmorphism (rgba(30, 41, 59, 0.7) with blur).
Layout: > - Left Sidebar (Col-3): Scenario Toggles (Bear/Base/Bull) and Range Sliders for inputs (Growth, Margin, PE, Volatility).
Right Main Area (Col-9): Top section for Chart.js Line Chart (Price & EPS). Middle section for a clean HTML Data Table (Projections). Bottom section for Monte Carlo Simulation.
Libraries: Use Tailwind CSS (CDN) and Chart.js (CDN). No other external dependencies.
Functionality:
Scenarios: Clicking Bear/Base/Bull must auto-update the sliders to predefined values.
Reactivity: Moving any slider must immediately re-render the table and charts without page reload.
Monte Carlo: Must run ~500 iterations in JS and display the 10th, 50th, and 90th percentile outcomes.
Data Injection:
Pre-fill the BASE_DATA object with the latest TTM financial data for [INSERT TICKER] which you will research now.
Ensure the 'Shares Outstanding' calculation logic approximates the current market cap.
Please generate the code now, strictly adhering to this visual style."

3. Technical Specs (The "DNA" of the App)
If building a custom GPT or AI Agent, paste this into its "Knowledge" or "System Instructions":
UI Framework:
Tailwind CSS for styling.
Custom CSS classes: .glass-panel for all containers.
Colors: Text is text-slate-300 for labels, text-white for values. Accents are Blue (Base), Green (Bull), Red (Bear).
JavaScript Logic Structure:
const BASE_DATA = { ... } : Holds the static TTM data.
const SCENARIOS = { ... } : Holds the preset assumptions for Bull/Bear/Base.
function calculateProjections() : Generates the 5-year forecast array.
function runMonteCarlo() : Uses Geometric Brownian Motion for risk simulation.
function updateModel() : The main controller that reads sliders and redraws UI.
HTML Structure:
Single file.
<style> block in head for custom overrides.
<script> block at the end of body for logic.
