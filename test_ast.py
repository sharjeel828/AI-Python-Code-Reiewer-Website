import ast
from analyzer import analyze_code
from ml_module import predict_vulnerabilities

# Test 1: Valid Code
code = """
def calculate_total(prices, tax_rate):
    total = 0
    for price in prices:
        if price > 0:
            total += price
    return total * (1 + tax_rate)
"""
print("--- Test 1: Valid Code ---")
res = analyze_code(code)
print(f"Metrics: {res['metrics']}")
predictions = predict_vulnerabilities(res['metrics'], res['issues'])
print(f"Risk Score: {predictions['risk_score']}")

# Test 2: Syntax Error Code
error_code = """
def broken_syntax(a, b)
    return a + b
"""
print("\n--- Test 2: Syntax Error ---")
res_error = analyze_code(error_code)
print(f"Errors: {res_error['errors']}")
