# Forecast mock data sourced from config/industry_data/*.json
# Fallback generator below

def generate_mock_forecast(industry_id: str):
    return {"info": f"Mock forecast for {industry_id}"}
