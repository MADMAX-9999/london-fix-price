import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def get_usd_to_eur_rate():
    # Pobierz aktualny kurs USD do EUR z Europejskiego Banku Centralnego (ECB)
    url = "https://api.exchangerate.host/latest?base=USD&symbols=EUR"
    response = requests.get(url)
    data = response.json()
    rate = data.get("rates", {}).get("EUR")
    if rate:
        return rate
    else:
        raise ValueError("Nie udało się pobrać kursu USD/EUR")

def scrape_london_fix_prices():
    url = "https://goldsilver.com/price-charts/historical-london-fix/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')
    if not table:
        print("Nie znaleziono tabeli z danymi London Fix.")
        return

    rows = table.find_all('tr')

    usd_to_eur = get_usd_to_eur_rate()
    print(f"Aktualny kurs USD → EUR: {usd_to_eur:.4f}")

    csv_file = "london_fix_prices_usd_eur.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Gold AM (USD)", "Gold AM (EUR)", 
                         "Gold PM (USD)", "Gold PM (EUR)", 
                         "Silver Noon (USD)", "Silver Noon (EUR)"])

        for row in rows[1:]:  # pomijamy nagłówek
            cols = row.find_all('td')
            if len(cols) >= 4:
                date = cols[0].text.strip()
                gold_am_usd = cols[1].text.strip().replace(',', '')
                gold_pm_usd = cols[2].text.strip().replace(',', '')
                silver_noon_usd = cols[3].text.strip().replace(',', '')

                # Konwersja na float, zabezpieczenie na puste lub brakujące dane
                def to_float(val):
                    try:
                        return float(val)
                    except:
                        return None

                gold_am_usd_f = to_float(gold_am_usd)
                gold_pm_usd_f = to_float(gold_pm_usd)
                silver_noon_usd_f = to_float(silver_noon_usd)

                gold_am_eur = round(gold_am_usd_f * usd_to_eur, 2) if gold_am_usd_f else ""
                gold_pm_eur = round(gold_pm_usd_f * usd_to_eur, 2) if gold_pm_usd_f else ""
                silver_noon_eur = round(silver_noon_usd_f * usd_to_eur, 2) if silver_noon_usd_f else ""

                writer.writerow([
                    date,
                    gold_am_usd, gold_am_eur,
                    gold_pm_usd, gold_pm_eur,
                    silver_noon_usd, silver_noon_eur
                ])

    print(f"Dane London Fix w USD i EUR zapisane do pliku {csv_file}")

if __name__ == "__main__":
    scrape_london_fix_prices()
