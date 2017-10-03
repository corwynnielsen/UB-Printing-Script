import sys
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def iprintanywhere_login(path, username, passwd):
    driver = webdriver.Chrome(path)
    driver.implicitly_wait(10)
    driver.get('https://iprintanywhere.buffalo.edu/cps/Login')

    driver.find_element_by_name('principal').send_keys(username)
    driver.find_element_by_name('credentials').send_keys(passwd)
    driver.find_element_by_name('Submit').click()

    return driver

def myiprint_login(driver, username, passwd):
    driver.get('https://myiprint.buffalo.edu:7773/user/signin.jsp')

    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').send_keys(passwd)
    driver.find_element_by_name('sign_in').click()

    return driver

def chose_printer(driver, printer):
    driver.find_element_by_partial_link_text(printer).click();

    return driver

def send_document(driver, filepath, ubit):
    driver.find_element_by_class_name('fileUpload').send_keys(filepath)
    driver.find_element_by_id('clientUID').send_keys(ubit)

    driver.find_element_by_name('Submit').click()
    driver.find_element_by_name('Submit').click()

    try:
        driver.switch_to.frame(driver.find_element_by_xpath(xpath="//iframe[1]"))
        #Need to sleep for 2 seconds to avoid throwing exception, selenium runs behind
        sleep(2)
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='glyphicons x3 green glyphicons-ok']")))
        driver.switch_to_default_content()
    except TimeoutException:
        print("Loading took too much time!")

    return driver

def release_prints(driver):
    for ele in driver.find_elements_by_name('print_job'):
        ele.click()

    driver.find_element_by_id('payPrintButton').click()

def main():

    ubit = sys.argv[1]
    passwd = sys.argv[2]
    filepath = sys.argv[3]
    chromedriver_path = sys.argv[4]

    # Log in to iprintanywhere
    driver = iprintanywhere_login(chromedriver_path, ubit, passwd)

    driver = chose_printer(driver, 'Capen')

    driver = send_document(driver, filepath, ubit)

    driver = myiprint_login(driver, ubit, passwd)

    driver = release_prints(driver)

    exit(0)








