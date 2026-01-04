# GVD Engine: Project Scope & Status Report
**Last Updated:** January 1, 2026
**Version:** 5.0 (Strategic Evaluation)

## 1. Project Vision
The **GVD Engine** (Grave Danger Engine) is an institutional-grade, agentic financial analysis platform. It moves beyond simple data aggregation to **adversarial verification** and **strategic synthesis**.

**Core Philosophy:**
*   **Adversarial Truth**: Data uses a "Short Seller" Auditor persona to challenge every extracted metric.
*   **Strategic Friction**: We don't just report numbers; we compare Management Narrative (Qual) vs Financial Data (Quant) to find "Thesis Friction".
*   **Transparency**: Every number is traceable to a Bounding Box (`[x,y,w,h]`) on the original source PDF.

---

## 2. High-Level Roadmap & Status

### Phase 1: The Foundation (Core Data & Valuation) [COMPLETE]
*   **Status**: Production Ready.
*   **Features**:
    *   `OriginatorAgent`: Scans sectors for new ideas.
    *   `ValuationEngine`: DCF, Gordon Growth, and 10-Year Glide Paths.
    *   `LogicGuard`: Prevents hallucinated target prices.

### Phase 2: The Body (Frontend & Robustness) [COMPLETE]
*   **Status**: Production Ready.
*   **Features**:
    *   Dash/Plotly Frontend with "Dark Mode" Institutional Aesthetic.
    *   `JobManager`: Async background processing.

### Phase 3: Forecasting & Modeling [COMPLETE]
*   **Status**: Production Ready.
*   **Features**:
    *   AI Analyst Reports generated from valuation models.
    *   Smart Defaults for historical growth/margins.

### Phase 4: Earnings Season (The Institutional Engine) [COMPLETE - ALPHA]
*   **Status**: **Useable Alpha**.
*   **Features**:
    *   **PDF Pipeline**: `Docling` (V2) based parsing with hierarchical table support.
    *   **Cross-Ref Indexer**: Maps "See Note X" citations.
    *   **Verification Loop**: Quant Agent extracts -> Auditor Agent verifies (with PyMuPDF JUMP) -> VLM verifies Cash Flows.
    *   **Dashboard**: Interactive PDF Viewer with visual overlays.

### Phase 5: Strategic Evaluation (Thesis Friction) [COMPLETE]
*   **Status**: **Live**.
*   **Features**:
    *   **Qual Agent (Anthropologist)**: Decodes MD&A Sentiment (Bullish/Bearish/Defensive).
    *   **Consolidator Agent**: Synthesizes "Thesis Friction" (Narrative vs Data).
    *   **UI Pivot**: Dashboard now displays a "Strategic Thesis" panel (Verdict, Conviction Score, Friction Analysis).

### Phase 6: Dynamic Integration & Polish [IN PROGRESS]
*   **Status**: **Active Development**.
*   **Focus**:
    *   Live Data integration.
    *   Production readiness (RAM optimization, Error Handling).

---

You can view the full frontend details here: **[DASHBOARD_ARCHITECTURE.md](project_docs/DASHBOARD_ARCHITECTURE.md)**

## 3. Active Workflows

| ID | Workflow Name | Description | Status |
| :--- | :--- | :--- | :--- |
| **A** | **New Idea Hunt** | "Find me a Compounder in BioTech". Scans sectors, filters, and models. | ✅ Live |
| **B** | **Earnings Season** | Upload 10-K -> Extract -> Audit -> Thesis. | ✅ Live (Alpha) |
| **C** | **Forecasting** | Deep-dive valuation modeling on existing holdings. | ✅ Live |
| **D** | **Strategy Console** | Portfolio rebalancing and optimization. | 🚧 UI Only |
| **E** | **Risk Report** | Macro stress testing (-20% crash simulation). | 🚧 Planned |
| **F** | **Radar** | Real-time news monitoring and early warning. | 🚧 Planned |
