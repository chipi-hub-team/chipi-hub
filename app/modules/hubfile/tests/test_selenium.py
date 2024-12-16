from selenium.common.exceptions import NoSuchElementException
import time

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


def test_hubfile_index():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the index page
        driver.get(f'{host}/hubfile')

        # Wait a little while to make sure the page has loaded completely
        time.sleep(4)

        try:

            pass

        except NoSuchElementException:
            raise AssertionError('Test failed!')

    finally:

        # Close the browser
        close_driver(driver)


def test_edit():
    driver = initialize_driver()
    driver.get("http://127.0.0.1:5000/")
    driver.set_window_size(912, 1028)
    driver.find_element(By.LINK_TEXT, "Login").click()
    driver.find_element(By.ID, "email").click()
    driver.find_element(By.ID, "email").send_keys("user1@example.com")
    driver.find_element(By.ID, "password").click()
    driver.find_element(By.ID, "password").send_keys("1234")
    driver.find_element(By.ID, "submit").click()
    driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
    driver.find_element(By.CSS_SELECTOR, ".hamburger").click()
    WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable((By.LINK_TEXT, "Home"))
    )
    driver.find_element(By.LINK_TEXT, "Home").click()
    driver.find_element(By.LINK_TEXT, "Sample dataset 3").click()
    driver.find_element(By.CSS_SELECTOR, ".list-group-item:nth-child(2) .col-12 > .btn:nth-child(1)").click()
    element = driver.find_element(By.CSS_SELECTOR, ".list-group-item:nth-child(2) .col-12 > .btn:nth-child(1)")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    element = driver.find_element(By.CSS_SELECTOR, "body")
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    driver.find_element(By.ID, "fileContentEdit").click()
    element = driver.find_element(By.ID, "fileContentEdit")
    driver.execute_script(
        "if(arguments[0].contentEditable === 'true') {arguments[0].innerText = 'adios'}",
        element
    )
    driver.find_element(By.CSS_SELECTOR, ".feather-save").click()


# Call the test function
test_hubfile_index()
test_edit()
