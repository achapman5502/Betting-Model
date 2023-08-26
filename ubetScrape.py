from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import csv
from selenium.common.exceptions import TimeoutException
import re


#split betting line into list
def split_text_into_columns(text):
    pattern = r'^(.*?) - (.*?) (.*?) \((.*?) vs (.*?)\) -'
    match = re.match(pattern, text)
    if match:
        return [match.group(1).strip(), match.group(2).strip(), match.group(3).strip(), match.group(4).strip(), match.group(5).strip()]
    else:
        return [""] * 5

#if odds are given as Pick-em
def convert_pk_to_numeric(text):
    if text.startswith("PK-"):
        return "-" + text[3:]
    elif text.startswith("PK+"):
        return "+" + text[3:]
    else:
        return text

#split bet into a string
def split_bet_string(text):
    start_index = 1
    end_index = len(text)
    if "+" in text:
        end_index = text.index("+")
    elif "-" in text:
        end_index = text.index("-")
    value = text[start_index:end_index]
    sign = text[end_index:]
    length = len(value)
    if value[length - 1] == "½":
        value = value[0: length - 1] + ".5"
    return value, sign


data_dict = {
    "Player Name": list(),
    "Bet Type": list(),
    "Measure": list(),
    "First Team" : list(),
    "Second Team" : list(),
    "Amount Ubet" : list(),
    "Over Odds Ubet" : list(),
    "Under Odds Ubet" : list(),
    "No Odds Ubet" : list(),
    "Yes Odds Ubet" : list()
}

DRIVER_PATH = ''
driver = webdriver.Chrome(executable_path=DRIVER_PATH)
#log in to website
driver.get('https://ubet.ag')
username = ""
password = ""

#log in to ubet.ag
driver.find_element("id", "username").send_keys(username)
driver.find_element("id", "password").send_keys(password)
driver.find_element("id", "login-account").click()

#click on baseball props
driver.find_element("name", "lg_11450").click()
driver.find_element("name", "lg_11826").click()
driver.find_element("name", "lg_1879").click()
driver.find_element("id", "ctl00_WagerContent_btn_Continue_top").click()


lines = driver.find_elements("class name", "line")
for line in lines:
    try:
        first_paragraph = line.find_element("class name", "col-md-12")
        text = first_paragraph.text
        #print(text)
        info = split_text_into_columns(text)
        wait = WebDriverWait(line, .1)
        twoNums = wait.until(EC.presence_of_all_elements_located((By.XPATH, ".//label[@class='btn btn-danger']")))
        if twoNums is not None and len(twoNums) == 2:
            if info[2] == "TO RECORD THE WIN":
                no = convert_pk_to_numeric(twoNums[0].text)
                yes = convert_pk_to_numeric(twoNums[1].text)
                data_dict["No Odds Ubet"].append(no)
                data_dict["Yes Odds Ubet"].append(yes)
                data_dict["Amount Ubet"].append("NA")
                data_dict["Over Odds Ubet"].append("NA")
                data_dict["Under Odds Ubet"].append("NA")
            else:
                over = split_bet_string(twoNums[0].text)
                under = split_bet_string(twoNums[1].text)
                tAmount = over[0]
                overLine = over[1]
                underLine = under[1]
                data_dict["Amount Ubet"].append(tAmount)
                data_dict["Over Odds Ubet"].append(overLine)
                data_dict["Under Odds Ubet"].append(underLine)
                data_dict["No Odds Ubet"].append("NA")
                data_dict["Yes Odds Ubet"].append("NA")

            data_dict["Player Name"].append(info[0])
            data_dict["Bet Type"].append(info[1])
            data_dict["Measure"].append(info[2])
            data_dict["First Team"].append(info[3])
            data_dict["Second Team"].append(info[4])
            df = pd.DataFrame(data_dict)
            df = df.astype(str)
            df.to_csv("ubet_props.csv", index=False, quoting=csv.QUOTE_NONE, encoding='utf-8')
    except TimeoutException:
        print("No odds. Skipping this line.")

driver.quit()