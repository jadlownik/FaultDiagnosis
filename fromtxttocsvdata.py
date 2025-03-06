import re
import csv

# Funkcja do odczytu danych z pliku
def read_data_from_file(filename="dupa"):
    with open(filename, 'r') as f:
        file_content = f.read()
    
    # Szukamy danych w formacie 'data = {...}'
    matches = re.findall(r"data\s*=\s*({.*?})", file_content, re.DOTALL)
    
    # Zwracamy listę słowników
    data_dicts = []
    for match in matches:
        data_dicts.append(eval(match))
    
    return data_dicts

# Funkcja do zapisania danych w formacie CSV
def save_data_to_csv(data_dicts, filename="output.csv"):
    if not data_dicts:
        print("Brak danych do zapisania.")
        return
    
    # Dynamicznie zbieramy wszystkie klucze ze wszystkich słowników w data_dicts
    fieldnames = set()
    for data in data_dicts:
        fieldnames.update(data.keys())
    
    # Otwarcie pliku CSV w trybie zapisu
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Zapisz nagłówki (klucze)
        writer.writeheader()
        
        # Zapisz dane
        for data in data_dicts:
            # Upewniamy się, że wszystkie dane mają te same klucze
            # Jeśli w słowniku brakuje jakiegoś klucza, ustawiamy jego wartość na None
            row = {key: data.get(key, None) for key in fieldnames}
            writer.writerow(row)

# Odczytujemy dane z pliku 'dupa'
data_dicts = read_data_from_file("result_18_02_21_18_14.txt")

# Jeżeli dane zostały znalezione, zapisujemy je do pliku CSV
if data_dicts:
    save_data_to_csv(data_dicts)
    print("Dane zostały zapisane do pliku output.csv.")
else:
    print("Nie znaleziono sekcji 'data' w pliku.")
