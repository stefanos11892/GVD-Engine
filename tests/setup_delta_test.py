import os
import sys
import logging
from fpdf import FPDF

# Setup Path
sys.path.append(os.getcwd())

def create_prior_pdf(filename="prior_year.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 1. Vagueness Target (Precise Number)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "We expect to save $50 million in operational costs next year through automation.")
    pdf.ln(5)
    
    # 2. Entropy Target (High Density)
    pdf.multi_cell(0, 10, "Segment A revenue was $10.5B, Segment B was $4.2B, and EBITDA margins expanded to 35%.")
    pdf.ln(5)

    # 3. Omission Target (Header)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Risk Factors", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "1. Supply Chain Disruption", ln=True)
    pdf.cell(0, 10, "2. Cryptocurrency Volatility", ln=True) # Target for removal
    
    pdf.output(filename)
    print(f"Created: {filename}")
    return filename

def create_current_pdf(filename="current_year.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 1. Vagueness Trigger (Retreat to qualifier)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "We expect to save a significant amount in operational costs next year through automation.")
    pdf.ln(5)
    
    # 2. Entropy Trigger (Low Density / Fluff)
    pdf.multi_cell(0, 10, "Segment revenue performance remained robust across various verticals, and margins demonstrated meaningful expansion due to synergies.")
    pdf.ln(5)

    # 3. Omission Trigger (Missing Crypto)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Risk Factors", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "1. Supply Chain Disruption", ln=True)
    # Crypto is gone
    
    pdf.output(filename)
    print(f"Created: {filename}")
    return filename

if __name__ == "__main__":
    create_prior_pdf()
    create_current_pdf()
