from undetected_chromedriver import Chrome, ChromeOptions
import json
import os, time

home_url = 'https://www.designgurus.io/'
course_url = 'https://www.designgurus.io/path/system-design-interview-playbook'

driver = Chrome()

def manual_login_and_save_cookies(driver, url):
    driver.get(home_url)
    input("Press Enter to continue...")  # wait for manual login
    driver.get(url)
    cookies = driver.get_cookies()
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f)
    print('Cookies saved')
    
def load_cookies(driver):
    if 'cookies.json' in os.listdir():
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print('Cookies loaded')
    driver.refresh()

# cookies = manual_login_and_save_cookies(driver, home_url)
# driver.get(course_url)
# input("Press Enter to continue...")  # wait 
# driver.get('https://www.designgurus.io/course-play/grokking-the-system-design-interview/doc/638c0b75ac93e7ae59a1b081')
# input("Press Enter to continue...")  # wait
# driver.quit()

"""
1. Another page in the same browser
2. Multi-processing
3. Auto login using CSS selector to post password
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


with open('login.json', 'r') as f:
    login = json.load(f)
    email = login[0]["email"]
    password = login[0]["password"]

# Navigate to the home page
driver.get(home_url)

# Click the login button (replace 'loginButtonSelector' with the actual selector)
WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cy='nav-login-btn']"))
).click_safe()


# Click on the Google login button
google_login_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Google Login']"))
)
google_login_button.click()

# Wait for the username field to be visible and enter the username
WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.ID, "identifierId"))
).send_keys(email)
# .find_element(By.XPATH, '//input[@id="identifierId"]')

# Click Next to proceed to the password field
WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
).click_safe()

# Enter password 
password_input = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.NAME, "Passwd"))
).send_keys(password)

# Click Next to proceed to finish login
driver.find_element(By.XPATH,  "//button[contains(., 'Next')]").click_safe()

input("Press Enter to continue...")  # wait 
driver.quit()
