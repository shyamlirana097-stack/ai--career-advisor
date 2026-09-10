import requests

COUNTRIES = {"germany": "DEU", "canada": "CAN", "usa": "USA",
             "australia": "AUS", "india": "IND"}
INDICATORS = {"gdp_growth": "NY.GDP.MKTP.KD.ZG",
              "inflation": "FP.CPI.TOTL.ZG",
              "unemployment": "SL.UEM.TOTL.ZS"}

def get_latest(code, indicator):
    url = f"https://api.worldbank.org/v2/country/{code}/indicator/{indicator}?format=json&per_page=5"
    data = requests.get(url, timeout=15).json()
    for entry in data[1]:                    # skip metadata, walk newest→oldest
        if entry["value"] is not None:
            return entry["date"], round(entry["value"], 2)
    return None, None

for country, code in COUNTRIES.items():
    print(f"\n{country.upper()}")
    for name, ind in INDICATORS.items():
        year, val = get_latest(code, ind)
        print(f"  {name}: {val}% ({year})")