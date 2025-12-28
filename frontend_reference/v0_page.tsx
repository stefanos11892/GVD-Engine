import { InvestmentThesisCard } from "@/components/investment-thesis-card"

export default function HomePage() {
    return (
        <main className="min-h-screen p-8" style={{ backgroundColor: "var(--bg-page)" }}>
            <link rel="stylesheet" href="/theme.css" />

            <div className="max-w-5xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold mb-2" style={{ color: "white", fontFamily: "var(--font-sans)" }}>
                        GVD Engine - Investment Analysis
                    </h1>
                    <p className="text-secondary" style={{ color: "var(--text-secondary)" }}>
                        Refined Investment Thesis Card - Higher Density, Improved Legibility
                    </p>
                </div>

                <InvestmentThesisCard
                    ticker="NVDA"
                    status="PASS"
                    narrative="Based on the live screen, I have identified NVDA as the top candidate. This list is dominated by magnificent growth companies, but applying the undervalued filter requires us to look for the least demanding price tag among the highest quality assets. NVIDIA, despite its rapid ascent, currently holds the lowest P/E ratio among the trillion-dollar technology giants on this screen. We are buying quality and dominance: the company is the essential infrastructure provider for the AI revolution, a structural growth theme that will run for decades. While the price is high by traditional measures, we pay for a proven compounder with an almost unassailable moat, ensuring that capital is continuously reinvested at extraordinary rates of return."
                    dealMemo={{
                        ticker: "NVDA",
                        marketCap: "4.65T",
                        pe: "191.32",
                        thesis:
                            "The Essential Toll Booth. NVDA possesses an unshakeable competitive position as the key supplier of foundational infrastructure (GPUs) necessary for Global AI deployment. The relative P/E (lowest among the $1T+ cohort on this screen) suggests the market is pricing in less future growth deceleration than its peers, making it the most attractive quality-growth investment on this specific list.",
                    }}
                />

                {/* Comparison: Show the before/after improvement */}
                <div
                    className="mt-8 p-6"
                    style={{
                        backgroundColor: "var(--bg-card)",
                        border: "1px solid var(--border-tech)",
                        borderRadius: "var(--radius-card)",
                    }}
                >
                    <h2 className="text-lg font-semibold mb-3" style={{ color: "white" }}>
                        Design Improvements
                    </h2>
                    <ul className="space-y-2 text-sm" style={{ color: "var(--text-secondary)" }}>
                        <li>✓ Metrics separated into dedicated grid layout with clear visual hierarchy</li>
                        <li>✓ Increased spacing between narrative and data sections for better scanability</li>
                        <li>✓ Thesis text in contained box with improved line-height for legibility</li>
                        <li>✓ Consistent use of monospace font for numerical data</li>
                        <li>✓ Reduced visual noise with subtle borders and backgrounds</li>
                        <li>✓ Higher information density while maintaining readability</li>
                    </ul>
                </div>
            </div>
        </main>
    )
}

