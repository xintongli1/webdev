from undetected_chromedriver import Chrome, ChromeOptions
import json
import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import base64

home_url = 'https://www.designgurus.io/'
course_url = 'https://www.designgurus.io/course/grokking-the-system-design-interview'
test_access_url = 'https://www.designgurus.io/course-play/grokking-the-system-design-interview/doc/638c0b75ac93e7ae59a1b071'

# headless mode doesn't work because Google blocks it from logging in
driver = Chrome()
# driver.set_window_size(1920, 1080) 

with open('login.json', 'r') as f:
    login = json.load(f)
    email = login[0]["email"]
    password = login[0]["password"]


def auto_login(driver, home_url, email, password, retry=3):
    """
    Auto login using CSS selector to post password
    """
    while retry > 0:
        try:
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
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')]"))
            ).click_safe()

            # Wait for the redirection and for the "Welcome" text to appear
            welcome_text_locator = (By.XPATH, "//div[contains(@class, 'homepage_homePage__title') and contains(text(), 'Welcome')]")

            # Set an explicit wait for the above condition to be met
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(welcome_text_locator)
            )
            print("Login succeeded")
            return 0
        except:
            # take screenshot
            driver.save_screenshot('login_failure_screenshot.png')
            print("Login failed")
            retry -= 1
    print("Failed to login after all retry attempts")
    return 1


def close_cookie_popup(driver):
    """
    Close the cookie popup if it appears
    """
    try:
        # Wait up to 10 seconds for the cookie pop-up to become visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-cy='accept-cookie-policy-btn']"))
        ).click()
        print("Cookie popup detected and closed.")
    except:
        # If the cookie pop-up does not appear within 10 seconds, print a message
        print("No cookie popup was detected.")


def get_course_content_url(driver: Chrome, course_url):
    """
    Given a course URL, return all the URLs of the course content page, and save to json file
    """
    try:
        driver.get(course_url)
        # Wait for the course page to load
        course_content_all = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'courseContent_courseContent__overviewWrapper')]"))
        )
    except:
        print("Failed to load the course page")

    close_cookie_popup(driver)

    # Expand all the chapters before getting the contents
    accordions = course_content_all.find_elements(By.XPATH, "//div[contains(@class, 'courseContent_courseContent__accordionSummary__ymvqW')]")
    for i, accordion in enumerate(accordions, start=1):
        if accordion.get_attribute('aria-expanded') == 'false':
            retry = 3
            while retry > 0:
                try:
                    # Scroll to the accordion and click on it
                    actions = ActionChains(driver)
                    actions.move_to_element(accordion).perform()
                    WebDriverWait(driver, 6).until(EC.element_to_be_clickable(accordion)).click()
                    print(f"Expanded the {i}-th accordion")
                    retry = 0    # break the loop
                except TimeoutException:
                    print(f"Timeout waiting for the {i}-th accordion")
                except StaleElementReferenceException:
                    print(f"The {i}-th accordion became stale")
                except Exception as e:
                    print(f"Failed to expand the {i}-th accordion: {e}")
                retry -= 1
    
    # Get the URLs of the course content pages
    course_content_all = driver.find_element(By.XPATH, "//div[contains(@class, 'courseContent_courseContent__overviewWrapper')]")
    chapter_elements = course_content_all.find_elements(By.XPATH, "div[contains(@class, 'MuiBox-root')]")
    for element in chapter_elements:
        try:
            # Get chapter title
            # Use a dot at the beginning of XPath to search within the context of the current element
            chapter_number = element.find_element(By.XPATH, ".//div[contains(@class, 'courseContent_courseContent__chapterNumber')]").text
            chapter_title = element.find_element(By.XPATH, ".//div[contains(@class, 'courseContent_courseContent__chapterTitle___WHOM')]").text
            chapter_name = chapter_number + " " + chapter_title  
            print(chapter_name)

            # Get the URLs of the chapter content pages
            chapter_documents = element.find_elements(By.XPATH, ".//a[contains(@class, 'courseContent_courseContent__documentTitleWrapper')]")
            print("Number of documents:", len(chapter_documents))
            for document in chapter_documents:
                document_url = document.get_attribute('href')
                document_title = document.find_element(By.XPATH, ".//div[contains(@class, 'courseContent_courseContent__documentTitle__xqObJ')]").text
                print(f"{document_title}: {document_url}")

        except Exception as e:  # It's better to catch specific exceptions, but for debugging, this is okay
            print("Error retrieving chapter information:", e)

        


def print_to_pdf(driver: Chrome, url):
    """
    Print the course content page to PDF
    """
    driver.get(url)

    time.sleep(8) # wait for the page to render

    # Click on "Got it" for cookie notice if available
    close_cookie_popup(driver)

    # Print the page to PDF
    result = driver.execute_cdp_cmd("Page.printToPDF", {
        "landscape": False,
        "displayHeaderFooter": False,
        "printBackground": True,
        "preferCSSPageSize": True,
    })

    # Get the PDF data and save it to a file
    pdf_data = result['data']
    with open('test.pdf', 'wb') as file:
        file.write(base64.b64decode(pdf_data))


if __name__ == "__main__":
    status_code = auto_login(driver, home_url, email, password)
    if status_code == 0:
        get_course_content_url(driver, course_url)
        # print_to_pdf(driver, test_access_url)
    driver.quit()



# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------

def manual_login_and_save_cookies(driver, url):
    """
    Deprecated
    Session cookies can not be used for auto login once the browser is closed.
    """
    driver.get(home_url)
    input("Press Enter to continue...")  # wait for manual login
    driver.get(url)
    cookies = driver.get_cookies()
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f)
    print('Cookies saved')
    
# Deprecated
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
