from dotenv import load_dotenv
import os

load_dotenv()

def predict_vulnerabilities(metrics, issues):
    """
    Mock ML processing module.
    Takes extracted static analysis features and returns dummy ML predictions.
    Combine this with the rule-based results.
    """
    predictions = {
        "ml_detected_issues": [],
        "risk_score": 0.0,
        "suggestions": []
    }
    
    # Calculate a mock risk score based on cyclomatic complexity and issues count
    complexity = metrics.get('cyclomatic_complexity', 1)
    num_issues = len(issues)
    
    # Mock formula
    risk = min(100.0, (complexity * 2.5) + (num_issues * 5.0))
    predictions["risk_score"] = round(risk, 2)
    
    if complexity > 10:
        predictions["ml_detected_issues"].append({
            "type": "High Complexity Pattern",
            "message": "The code pattern indicates potentially unmaintainable and highly coupled logic.",
            "severity": "high"
        })
        predictions["suggestions"].append("Consider breaking down functions with high branch counts into smaller, pure functions.")
        
    if num_issues > 5:
        predictions["ml_detected_issues"].append({
            "type": "Code Smell Density",
            "message": "High density of style or syntax issues detected, suggesting rushed implementation.",
            "severity": "medium"
        })
        predictions["suggestions"].append("Run an auto-formatter like black before committing to standardize the codebase.")
        
    if metrics.get('depth_of_nested_blocks', 0) > 4:
         predictions["ml_detected_issues"].append({
            "type": "Deep Nesting",
            "message": "Model detected arrow anti-pattern (excessive nesting).",
            "severity": "medium"
        })
         predictions["suggestions"].append("Use early returns or guard clauses to reduce nesting depth.")

    # Always return some positive reinforcement if risk is low
    if risk < 20.0 and len(predictions["ml_detected_issues"]) == 0:
         predictions["suggestions"].append("Code looks clean and low-risk based on our model's historical data.")
         
    return predictions

def generate_corrected_code(original_code, detected_issues):
    """
    Calls Groq LLM API to fix bugs based on a strict system prompt.
    Includes retry logic for rate limits and token optimization.
    """
    import time
    
    # 1. Truncate original code if it's excessively large to stay within free tier limits
    MAX_CHARS = 8000 
    if len(original_code) > MAX_CHARS:
        original_code = original_code[:MAX_CHARS] + "\n# ... [code truncated for length] ..."

    error_messages = [issue.get("message", "") for issue in detected_issues if issue.get("severity") == "error" or issue.get("type") == "SyntaxError"]
    error_message = " | ".join(error_messages) if error_messages else "Syntax or structural issues detected."
    
    max_retries = 3
    retry_delay = 5 # seconds
    
    for attempt in range(max_retries):
        try:
            from groq import Groq
            
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable not set.")
                
            client = Groq(api_key=api_key)
            
            system_prompt = "You are an expert Python debugger. Fix any typos, syntax errors, or logical bugs. Return ONLY the raw, corrected Python code. No markdown, no explanations."
            user_prompt = f"Error Message:\n{error_message}\n\nBroken Code:\n{original_code}"
            
            # Reducing max_tokens significantly helps avoid TPM rate limits on Groq free tier
            # Most code fixes don't need 4096 tokens.
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=1024, 
            )
            
            fixed_code = completion.choices[0].message.content
            fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()
            
            if not fixed_code:
                return "Error generating fix. Please try again."
                
            return fixed_code
            
        except Exception as e:
            error_str = str(e).lower()
            # If it's a rate limit error, wait and retry
            if "rate_limit_exceeded" in error_str or "429" in error_str:
                if attempt < max_retries - 1:
                    print(f"Rate limit hit. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
            
            print(f"CRITICAL GROQ API ERROR: {str(e)}")
            return f"Error generating fix: {str(e)}"
    
    return "Error: Maximum retries exceeded due to rate limits. Please try again in a minute."

