from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from collections import defaultdict
import json

import os
os.popen('paplay mixkit-slot-machine-payout-alarm-1996.wav').read()

is_more_than_50000 = False
last_value = None

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = ''  # Replace with your actual bot token
TELEGRAM_CHAT_ID = ''  # Replace with your actual chat ID

def send_telegram_message(message):
    """
    Send a message to a Telegram chat using the Bot API.
    
    :param message: The message to send
    """
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    params = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # Optional: allows formatting
    }
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return None
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize the Selenium WebDriver (replace 'chromedriver' with your browser's driver if not using Chrome)
driver = webdriver.Chrome()


while True:
    try:
        # Open the target URL
        driver.get("https://data.asxn.xyz/dashboard/hl-spot-ecosystem")
        wait = WebDriverWait(driver, 20)
        relem = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[1]/div[2]/div/table/tbody/tr[2]'))  # Adjust the XPath if necessary
        )
        table_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div[2]'))  # Adjust the XPath if necessary
        )
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "twap-table")))
        
        dropdown = Select(driver.find_element(By.CLASS_NAME, 'rows-per-page-select'))
        # print(dropdown)
        dropdown.select_by_visible_text('All') 

        # Find the rows in the table body
        rows = table.find_elements(By.XPATH, ".//tbody/tr")

        # Extract headers from the table
        headers = [header.text for header in table.find_elements(By.XPATH, ".//thead/tr/th")]

        # Extract table data
        table_data = []
        for row in rows:
            row_data = []
            cells = row.find_elements(By.TAG_NAME, "td")
            for cell in cells:
                # If the cell contains a link, extract the link and the text
                link_element = cell.find_element(By.TAG_NAME, "a") if cell.find_elements(By.TAG_NAME, "a") else None
                if link_element:
                    row_data.append(f"{cell.text} ({link_element.get_attribute('href')})")
                else:
                    row_data.append(cell.text)
            table_data.append(row_data)
            
        def time_to_minutes(time_str):

            """
            Convert a time string like '4 h', '5h 30m', etc., to minutes.
            
            :param time_str: String representing time in the format '<X> h <Y> m', '<X>h', or '<Y> m'.
            :return: Total time in minutes as an integer.
            """
            hours, minutes = 0, 0
            print(time_str)
            if time_str.endswith('h'):
                return int(time_str[:-1]) * 60
            
            # Split the string into components
            components = time_str.split()
            ln = len(components)
            tot = 0
            for i in range(ln):
                if 'h' == components[i][-1]:
                    tot += int(components[i][:-1]) * 60
                elif 'm' == components[i][-1]:
                    tot += int(components[i][:-1]) 

            # Calculate total minutes
            
            return tot


        tot = 0
        yo = table_data

        from collections import defaultdict

        d = defaultdict(lambda:0)
        drug_hype = []

        for i in yo:
            if True:
                z = i[3]
                z = z[1:]
                
                if 'K' in z:
                    z = float(z[:-1]) * 1000
                elif 'M' in z:
                    z = float(z[:-1]) * 1000000
                else:
                    z = float(z)
                komtol = i[-1].split('\n')[-1]
                # drug_hype.append((z * (1 / time_to_minutes(i[5])), time_to_minutes(i[5]), komtol))
                if i[0] == 'BUY':
                    d[i[1]] += z * (1 / time_to_minutes(i[5]))
                    if i[1] == 'HYPE':
                        drug_hype.append((z * (1 / time_to_minutes(i[5])), time_to_minutes(i[5]), komtol))
                else:
                    d[i[1]] -= z * (1 / time_to_minutes(i[5]))
                    if i[1] == 'HYPE':
                        drug_hype.append((-z * (1 / time_to_minutes(i[5])), time_to_minutes(i[5]), komtol))
                # print(1/time_to_minutes(i[5])
                
        send_telegram_message(json.dumps(d))
        if d['HYPE'] > 50000:
            if is_more_than_50000 is not True:
                import os
                os.popen('paplay mixkit-slot-machine-payout-alarm-1996.wav').read()
            is_more_than_50000 = True
            send_telegram_message('> 50k bps BUY HYPE NOW (perhaps)')
        else:
            is_more_than_50000 = False
        if d['HYPE'] < 0:
            drug_hype = sorted(drug_hype)
            print(drug_hype)
            send_telegram_message(json.dumps(drug_hype[:10]))
        else:
            drug_hype = sorted(drug_hype)
            print(drug_hype)
            send_telegram_message(json.dumps(drug_hype[-10:]))
        if last_value == None:
            last_value = d['HYPE']
        else:
            if last_value < 0 and d['HYPE'] > 0:
                os.popen('paplay mixkit-rooster-crowing-in-the-morning-2462.wav').read()    
            elif last_value > 0 and d['HYPE'] < 0:
                os.popen('paplay mixkit-classic-alarm-995.wav').read()
            last_value = d['HYPE']
        time.sleep(10)
    except Exception as e: 
        print(e)
        pass
