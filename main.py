from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.nba.com/stats/players')

driver.maximize_window()

wait = WebDriverWait(driver, 10)

try:
    decline = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#onetrust-reject-all-handler')))
    decline.click()
except:
    pass

time.sleep(1)
all_players_stats = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'See All Player Stats')))
all_players_stats.click()

per_game = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div[3]/section[1]/div/div/div[3]/label/div/select/option[2]')))
per_game.click()

body = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.Crom_body__UYOcU tr')))

class_to_remove = 'Crom_stickySecondColumn__29Dwf'
player_names = []
for row in body:
    tds = row.find_elements(By.TAG_NAME, 'td')
    for td in tds:
        if class_to_remove in td.get_attribute('class').split():
            player_names.append(td.text)
            driver.execute_script("""
                var td = arguments[0];
                td.parentNode.removeChild(td);
            """, td)
            break

head = driver.find_elements(By.CSS_SELECTOR, '.Crom_headers__mzI_m th')
visible_head = [th for th in head if th.is_displayed()]

list_of_lists_body = []
for row in body:
    listt = row.text.split(' ')[1:]
    list_of_lists_body.append(listt)

list_head = [th.text for th in visible_head][1:]

for i in range(len(list_of_lists_body)):
    list_of_lists_body[i].insert(0, player_names[i])

df = pd.DataFrame(list_of_lists_body, columns=list_head)

df.to_csv("top_50_nba_players_stats.csv", index=False)
print(df)

driver.quit()
