interface DealMemoData {
    ticker: string
    marketCap: string
    pe: string
    thesis: string
}

interface InvestmentThesisProps {
    ticker: string
    status: "PASS" | "FAIL" | "HOLD"
    narrative: string
    dealMemo: DealMemoData
}

export function InvestmentThesisCard({ ticker, status, narrative, dealMemo }: InvestmentThesisProps) {
    const statusDotClass = status === "PASS" ? "dot-green" : status === "FAIL" ? "dot-red" : "dot-amber"

    return (
        <div className="card-principal">
            <div className="card-principal-header">
                <div className="flex items-center justify-between">
                    <span>Investment Thesis</span>
                    <div className="badge-status-dot">
                        <span className={`dot ${statusDotClass}`} />
                        {status}
                    </div>
                </div>
            </div>

            <div className="card-principal-body">
                {/* Narrative Section - Condensed */}
                <div className="mb-6 pb-6" style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <p className="text-body-technical leading-relaxed">{narrative}</p>
                </div>

                {/* Deal Memo Section - High Density Grid */}
                <div className="space-y-4">
                    <h3 className="text-label mb-4">Deal Memo</h3>

                    {/* Metrics Grid - Separated from Thesis */}
                    <div
                        className="grid grid-cols-3 gap-6 mb-6 p-5"
                        style={{
                            backgroundColor: "rgba(2, 6, 23, 0.5)",
                            borderRadius: "8px",
                            border: "1px solid var(--border-subtle)",
                        }}
                    >
                        <div className="space-y-1.5">
                            <div className="text-label text-[11px]">Ticker</div>
                            <div className="font-mono text-xl font-bold text-white tracking-tight">{dealMemo.ticker}</div>
                        </div>
                        <div className="space-y-1.5">
                            <div className="text-label text-[11px]">Market Cap</div>
                            <div className="text-value text-xl font-semibold">{dealMemo.marketCap}</div>
                        </div>
                        <div className="space-y-1.5">
                            <div className="text-label text-[11px]">P/E Ratio</div>
                            <div className="text-value text-xl font-semibold">{dealMemo.pe}</div>
                        </div>
                    </div>

                    {/* Thesis Statement - Clearly Separated with Better Typography */}
                    <div className="space-y-3">
                        <div className="text-label text-[11px]">Thesis</div>
                        <div
                            className="p-5 leading-relaxed"
                            style={{
                                backgroundColor: "rgba(30, 41, 59, 0.3)",
                                borderRadius: "8px",
                                border: "1px solid var(--border-tech)",
                                fontSize: "0.9rem",
                                lineHeight: "1.7",
                                color: "var(--text-primary)",
                            }}
                        >
                            {dealMemo.thesis}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
