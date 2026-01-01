import json
import os
from extraction import scrape_oddsportal_results
from time import sleep

# =============================
# 1. Paramètres
# =============================
START_SEASON = 2006
END_SEASON = 2025  # dernière saison incluse, adapte si nécessaire
BASE_URL = "https://www.oddsportal.com/football/france/ligue-1-{season}/results/#/page/{page}/"
OUTPUT_DIR = "results"  # dossier pour sauvegarder les JSON
SLEEP_BETWEEN_PAGES = 2  # secondes pour éviter blocage

# Création du dossier si nécessaire
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================
# 2. Boucle sur les saisons
# =============================
for year in range(START_SEASON, END_SEASON + 1):
    # Format de saison 2006/2007
    season_str = f"{year}-{year+1}"
    print(f"Scraping Ligue 1 Saison {season_str} ...")

    all_matches = []
    page = 1
    while True:
        url = BASE_URL.format(season=f"{year}-{year+1}", suffix="", page=page)
        print(f"  Page {page}: {url}")

        matches = scrape_oddsportal_results(url)
        if not matches:
            print("  Aucun match trouvé, fin de la saison.")
            break

        all_matches.extend(matches)
        page += 1
        sleep(SLEEP_BETWEEN_PAGES)

    # Sauvegarde JSON par saison
    output_file = os.path.join(OUTPUT_DIR, f"ligue1_{season_str}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=4)

    print(f"  {len(all_matches)} matchs sauvegardés dans {output_file}\n")

print("Scraping terminé pour toutes les saisons !")
