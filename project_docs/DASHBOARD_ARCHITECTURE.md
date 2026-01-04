# GVD Engine: Dashboard Architecture
**Last Updated:** January 1, 2026

## 1. Core Framework
The Frontend is built on **Plotly Dash** using **Dash Bootstrap Components (DBC)** for a responsive, "Institutional Dark Mode" aesthetic.

*   **Entry Point**: `src/dashboard/app.py`
    *   Initializes `Dash(use_pages=True)`.
    *   Registers Callbacks (`register_earnings_callbacks`, `register_upload_callbacks`).
    *   Defines the Main Layout (Sidebar + Page Container).

## 2. Page Hierarchy
Files located in `src/dashboard/pages/`:

### A. Command Center (`/`) - `home.py`
The "Landing Page". It acts as a Launchpad for all workflows.
*   **Workflow Cards**: "New Idea Hunt", "Earnings Season", "Deep Dive".
*   **Risk & Monitoring**: "Risk Report", "News Radar".
*   **Quick Chat**: Placeholder for direct Agent interaction.

### B. Portfolio (`/portfolio`) - `portfolio.py`
Live view of the user's holdings.
*   **Data Source**: `src/utils/data_manager.py` (Loads `master_portfolio.csv`).
*   **Features**:
    *   **KPI Cards**: Total Value, Cash Balance, Invested Capital.
    *   **Holdings Grid**: AgGrid interactive table.
    *   **Allocation Chart**: Plotly Pie Chart.
    *   **Statement Upload**: Drag-and-drop PDF ingestion to update holdings.

### C. Workflows
Specific pages for active workflows (in `pages/workflows/`):
*   **Earnings Season (`/workflows/earnings`)**: The Interactive PDF Viewer and Thesis Dashboard.
*   **Forecasting (`/workflows/forecasting`)**: DCF Modeling UI.
*   **Radar (`/workflows/radar`)**: News monitoring feed (UI Concept).

---

## 3. Component Architecture
*   **Sidebar**: `src/dashboard/components/sidebar.py`. Navigation menu.
*   **Cards**: `src/dashboard/components/cards.py`. Reusable KPI metric cards.
*   **Callbacks**:
    *   `earnings_callbacks.py`: Handles complex PDF rendering, verifying metrics, and updating the Thesis UI.
    *   `data_callbacks.py`: Handles generic data refreshing.
    *   `upload_callbacks.py`: Handles file ingestion.

## 4. Design System
*   **Theme**: `dbc.themes.BOOTSTRAP` with custom CSS overrides (`assets/style.css` assumed).
*   **Colors**: Dark Mode (Background `#0a0a0a`, Accent Primary `#0d6efd`, Success `#198754`, Warning `#ffc107`).
