import requests
from bs4 import BeautifulSoup
import csv

url = "https://www.kitco.com/price/precious-metals?Currency=EUR"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
response.encoding = "utf-8"
soup = BeautifulSoup(response.text, 'html.parser')

# Znajdź tabelę z London Fix Price (zwykle ma id lub klasę, trzeba sprawdzić w inspektorze)
# Na stronie Kitco ceny London Fix są w sekcji z nagłówkami "London Fix"
# Przykład: znajdź wszystkie wiersze tabeli z cenami London Fix w EUR

# Szukamy sekcji z London Fix
section = soup.find('section', id='london-fix-section')  # przykładowy id, trzeba zweryfikować

if not section:
    # Jeśli nie ma sekcji o takim id, szukamy alternatywnie po nagłówku
    headers = soup.find_all(['h2', 'h3'])
    section = None
    for h in headers:
        if 'London Fix' in h.text:
            # szukamy następnego rodzeństwa będącego tabelą
            sibling = h.find_next_sibling('table')
            if sibling:
                section = sibling
                break

if not section:
    print("Nie znaleziono sekcji London Fix na stronie")
    exit()

table = section if section.name == 'table' else section.find('table')
if not table:
    print("Nie znaleziono tabeli z London Fix")
    exit()

rows = table.find_all('tr')

# Przygotowanie do zapisu CSV
csv_file = "london_fix_prices_eur.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Metal", "Fix Type", "Price 1 (EUR)", "Price 2 (EUR, optional)"])

    for row in rows[1:]:  # pomijamy nagłówek tabeli
        cols = row.find_all('td')
        if len(cols) >= 3:
            metal = cols[0].text.strip()
            fix_type = cols[1].text.strip()
            price1 = cols[2].text.strip()
            price2 = cols[3].text.strip() if len(cols) > 3 else ""
            writer.writerow([metal, fix_type, price1, price2])

print(f"Dane London Fix w EUR zapisane do pliku {csv_file}")
