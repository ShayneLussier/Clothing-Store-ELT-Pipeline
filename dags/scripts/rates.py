import requests
from datetime import datetime

# -------------------- FUNCTIONS -------------------- #

# Retrieve exchange rates based on €EURO
def api_date(date):
    date_obj = datetime.strptime(date, "%Y%m%d")
    formatted_date = date_obj.strftime("%Y-%m-%d")
    return formatted_date

def retrieve_inr_to_cad_rate(date):
    url_eur_exchange_rates = f'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/eur.json'
    response = requests.get(url_eur_exchange_rates)

    if response.status_code == 200:
        exchange_rates = response.json()
        inr_rate = float(exchange_rates['eur']['inr'])
        cad_rate = float(exchange_rates['eur']['cad'])

        # Convert Euro rates to INR:CAD
        inr_to_cad_rate = cad_rate / inr_rate
        return inr_to_cad_rate

def convert_to_cad(amount, rate):
        cad_amount = round((amount * rate), 2)
        return cad_amount