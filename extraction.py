import time
import json
from datetime import datetime
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def scrape_oddsportal_results(url: str, sleep_load: int = 4, sleep_scroll: int = 2):
    """
    Scrap datas of OddsPortal based on an url and parse it

    Parameters
    ----------
    url : str
        URL OddsPortal
    sleep_load : int
        initial loading time
    sleep_scroll : int
        loading time between scroll for lazy loading

    Returns
    -------
    list[dict]
        Extracted matches
    """

    # =============================
    # 1. Selenium
    # =============================

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get(url)
        time.sleep(sleep_load)

        # =============================
        # 2. Scroll lazy loading
        # =============================

        last_height = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_scroll)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html = driver.page_source

    finally:
        driver.quit()

    # =============================
    # 3. Parsing
    # =============================

    soup = BeautifulSoup(html, "html.parser")

    matches = []
    current_date = None

    # =============================
    # 4. Parcours
    # =============================

    for event in soup.find_all("div", class_="eventRow"):

        # ---- DATE HEADER ----
        date_div = event.find("div", {"data-testid": "date-header"})
        if date_div:
            txt = date_div.get_text(strip=True)
            try:
                current_date = datetime.strptime(txt, "%d %b %Y").date()
            except ValueError:
                continue

        # ---- MATCH ROW ----
        game_row = event.find("div", {"data-testid": "game-row"})
        if not game_row or current_date is None:
            continue

        # URL match
        a = game_row.find("a", href=True)
        if not a:
            continue
        match_url = "https://www.oddsportal.com" + a["href"]

        # Teams
        teams = game_row.find_all("p", class_="participant-name")
        if len(teams) != 2:
            continue

        team_1 = teams[0].get_text(strip=True)
        team_2 = teams[1].get_text(strip=True)

        # Score 
        score = {"1": None, "2": None}
        score_divs = game_row.select("div.ml-auto.mr-3.flex.font-bold")
        if len(score_divs) >= 2:
            score["1"] = int(score_divs[0].get_text(strip=True))
            score["2"] = int(score_divs[1].get_text(strip=True))

        # Odds
        odds_vals = []
        for p in event.find_all("p"):
            try:
                odds_vals.append(float(p.get_text(strip=True)))
            except ValueError:
                continue

        odds = {"1": None, "X": None, "2": None}
        if len(odds_vals) >= 3:
            odds["1"], odds["X"], odds["2"] = odds_vals[:3]

        # Winner
        winner = None
        if score["1"] is not None:
            if score["1"] > score["2"]:
                winner = "1"
            elif score["2"] > score["1"]:
                winner = "2"
            else:
                winner = "X"

        matches.append({
            "date": current_date.isoformat(),
            "team_1": team_1,
            "team_2": team_2,
            "score": score,
            "odds": odds,
            "winner": winner,
            "url": match_url
        })

    return matches


