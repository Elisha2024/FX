import requests
from decouple import config

def get_conversion_rate(base_currency, target_currency, amount):
    # Fetch the API key from the .env file
    api_key = config('ACCESS_TOKEN')
    
    # Construct the external API URL
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"

    try:
        response = requests.get(url, verify=False)
        
        # Check if the response status is successful
        if response.status_code == 200:
            response_data = response.json()
            exchange_rates = response_data.get("conversion_rates", {})
            rate = exchange_rates.get(target_currency)
            
            # Check if the rate exists and is valid
            if rate is not None:
                converted_amount = float(amount) * float(rate)
                
                return {
                    "converted_amount": converted_amount,
                    "rate": rate
                }
            else:
                return {"error": f"Conversion rate for {target_currency} not available."}
        else:
            return {"error": f"Failed to fetch data from the API. Status code: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}



def get_currency_codes():
    api_key = config('ACCESS_TOKEN') 
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"

    try:
        response = requests.get(url, verify=False)
        
        if response.status_code != 200:
            return {"error": "Failed to retrieve currency codes.", "status_code": response.status_code}
        
        data = response.json()
        if 'conversion_rates' not in data:
            return {"error": "Currency data not available."}

        currencies = list(data['conversion_rates'].keys())
        return {"currencies": currencies}
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
