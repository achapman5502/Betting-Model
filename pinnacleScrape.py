from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import csv
from selenium.common.exceptions import TimeoutException
import re
from selenium.webdriver.common.action_chains import ActionChains

def split_description(description):
    parts = description.split("(")
    name = parts[0].strip()
    prop = parts[1][:-1].strip()
    return name, prop

def extract_number(string):
    pattern = r'(\d+(\.\d+)?)' 
    matches = re.findall(pattern, string)
    if matches:
        return float(matches[0][0])
    else:
        return None

data_dict = {
    "Player Name": list(),
    "Metric": list(),
    "Amount" : list(),
    "Over Odds" : list(),
    "Under Odds" : list(),
}

DRIVER_PATH = ''
driver = webdriver.Chrome(executable_path=DRIVER_PATH)


games = []


for game in games:
    driver.get(game)
    wait = WebDriverWait(driver, 100)
    main = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'style_marketGroups__3cMM3')))
    lines = main.find_elements("class name", "style_primary__1bqk9")
    for line in lines:
        #find player name and bet type
        player_name = line.find_element(By.XPATH, './/div[@class="style_title__3SfDM collapse-title style_collapseTitle__Qul74"]/span')
        player = player_name.text
        #find the over/under amount
        amounts = line.find_elements("class name", "style_label__2rlQp")
        #find the odds on over and under
        odds = line.find_elements("class name", "style_price__3LrWW")
        #split player into player name and prop
        vars = split_description(player)
        playerName = vars[0]
        prop = vars[1]
        #get the over/under number
        if amounts is not None and len(amounts) > 0:
            number = extract_number(amounts[0].text)
            #append the values to the dictionary
            data_dict["Player Name"].append(playerName.upper())
            data_dict["Metric"].append(prop)
            data_dict["Amount"].append(number)
            data_dict["Over Odds"].append(odds[0].text)
            data_dict["Under Odds"].append(odds[1].text)
            df = pd.DataFrame(data_dict)
            df = df.astype(str)
            df.to_csv("pinnacle_props.csv", index=False, quoting=csv.QUOTE_NONE, encoding='utf-8')

driver.quit()