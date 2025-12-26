from src.dashboard.pages.workflows.forecasting import update_simulation
import dash.html as html

def test_pe_slider_impact():
    # Mock Data
    data = {
        "ticker": "TEST", 
        "current_price": 100, 
        "eps": 4.0, 
        "metrics": {"revenue": 1000, "net_income": 400}
    }
    
    # Run 1: PE = 5
    # method='pe'
    # peg=1.5 (default) -> Target PE = 15 * 1.5 = 22.5 (Overrides 5)
    print("--- Running Test 1 (PE=5) ---")
    fig1, _, _, _ = update_simulation(
        growth=0.15, margin=0.20, pe_override=5, vol=0.35, peg=1.5, method="pe", data=data
    )
    price1 = fig1.data[0].y[0] # Year 0 Price
    
    # Run 2: PE = 99
    print("--- Running Test 2 (PE=99) ---")
    fig2, _, _, _ = update_simulation(
        growth=0.15, margin=0.20, pe_override=99, vol=0.35, peg=1.5, method="pe", data=data
    )
    price2 = fig2.data[0].y[0]
    
    print(f"Price (PE=5): {price1}")
    print(f"Price (PE=99): {price2}")
    
    if price1 == price2:
        print("FAIL: Prices are identical. Slider is ignored.")
    else:
        print("PASS: Prices differ. Slider works.")

if __name__ == "__main__":
    test_pe_slider_impact()
