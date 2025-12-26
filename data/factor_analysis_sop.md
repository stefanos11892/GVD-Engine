# EQUITY FACTOR ANALYSIS PROTOCOL

## PHASE 1: DATA GATHERING (Use Search Tool)
Do not use Python for this step. Use your browsing tool to find today's % change for:
- SPY (Market)
- TLT (Rates)
- VTV (Value) & VUG (Growth)
- MTUM (Momentum)
- IWM (Small Cap)
- SPHB (High Beta) & SPLV (Low Vol)

## PHASE 2: CALCULATIONS (Use Python Tool)
Once you have the data from Phase 1, write a Python script to calculate these spreads:
1. Value_Spread = VTV_Change - VUG_Change
2. Size_Spread = IWM_Change - SPY_Change
3. Momentum_Spread = MTUM_Change - SPY_Change
4. Risk_Spread = SPHB_Change - SPLV_Change

## PHASE 3: INTERPRETATION LOGIC
- If Value_Spread > 0.50%: Tag as "Value Rotation"
- If Momentum_Spread < -0.50%: Tag as "Momentum Crash"
- If TLT_Change < -0.50% AND VUG_Change < 0: Tag as "Rate-Driven Selloff"

## PHASE 4: REPORTING
Generate a concise markdown report summarizing the "Mood of the Market" and any specific factor rotations observed.
