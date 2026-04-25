from langchain_core.tools import tool

@tool
def calculate_emi(principal: float, annual_rate: float, tenure_years: int):
    """Calculates monthly installment for a loan."""
    r = annual_rate / (12 * 100)
    n = tenure_years * 12
    emi = (principal * r * (1 + r)**n) / ((1 + r)**n - 1)
    return f"Monthly EMI: ₹{round(emi, 2)}"

@tool
def calculate_sip(monthly_investment: float, expected_return_rate: float, years: int):
    """Calculates future value of a Mutual Fund SIP."""
    i = expected_return_rate / (12 * 100)
    n = years * 12
    fv = monthly_investment * (((1 + i)**n - 1) / i) * (1 + i)
    return  f"Future Value: ₹{round(fv, 2)}"
