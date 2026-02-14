# Pricing per 1M tokens (USD)
# As of late 2024 / early 2025 estimates
PRICING = {
    # Groq (Free tier exists, but for estimation)
    "llama3-8b-8192": {"input": 0.05, "output": 0.08}, 
    "llama3-70b-8192": {"input": 0.59, "output": 0.79},
    "mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
    "gemma-7b-it": {"input": 0.07, "output": 0.07},
    # OpenAI
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the estimated cost of a request.
    """
    # Normalize model name slightly to match keys
    model_key = model.lower()
    # Partial match setup
    price_info = None
    for key in PRICING:
        if key in model_key:
            price_info = PRICING[key]
            break
            
    if not price_info:
        return 0.0
        
    input_cost = (input_tokens / 1_000_000) * price_info["input"]
    output_cost = (output_tokens / 1_000_000) * price_info["output"]
    
    return round(input_cost + output_cost, 6)
