from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver

from selenium.webdriver.common.by import By


def test_rating_index():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the index page
        driver.get(f'{host}/rating')

        # Wait a little while to make sure the page has loaded completely
        time.sleep(1)

        try:

            pass

        except NoSuchElementException:
            raise AssertionError('Test failed!')

    finally:

        # Close the browser
        close_driver(driver)


def test_rating_button_not_appear_no_login():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the index page
        driver.get(f'{host}')

        # Wait a little while to make sure the page has loaded completely
        time.sleep(1)

        driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()

        # Assert button not appear
        try:
            driver.find_element(By.XPATH, "//*[contains(@id, 'rating-button-')]")
            raise AssertionError('Rating button should not appear if user is not logged in')
        except NoSuchElementException:
            pass

    finally:

        # Close the browser
        close_driver(driver)


def test_rating_button_appear_logged():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the index page
        driver.get(f'{host}')

        # Wait a little while to make sure the page has loaded completely
        time.sleep(1)

        # Open the login page
        driver.get(f"{host}/login")

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Send the form
        password_field.send_keys(Keys.RETURN)

        driver.get(f"{host}/doi/10.1234/dataset4/")

        # Assert button appear

        try:
            driver.find_element(By.XPATH, "//*[contains(text(), 'Star')]")
        except NoSuchElementException:
            raise AssertionError('Rating button should appear if user is logged in')

    finally:

        # Close the browser
        close_driver(driver)


def test_rating_button_change():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        # Open the index page
        driver.get(f'{host}')

        # Wait a little while to make sure the page has loaded completely
        time.sleep(1)

        # Open the login page
        driver.get(f"{host}/login")

        # Find the username and password field and enter the values
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        # Send the form
        password_field.send_keys(Keys.RETURN)

        driver.get(f"{host}/doi/10.1234/dataset4/")

        # Assert button change

        try:
            star = driver.find_element(By.XPATH, "//*[contains(text(), 'Star')]")

            # get parent
            button = star.find_element(By.XPATH, "..")
            button.find_element(By.XPATH, "//*[contains(text(), '0')]")

            button.click()

            button.find_element(By.XPATH, "//*[contains(text(), '1')]")

        except NoSuchElementException:
            raise AssertionError('Rating button should change')

    finally:

        # Close the browser
        close_driver(driver)


# Call the test function
test_rating_index()
test_rating_button_not_appear_no_login()
test_rating_button_appear_logged()
test_rating_button_change()
