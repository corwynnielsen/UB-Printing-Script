import argparse
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

"""
Helps automate the printing process outside of UB's computers.
"""

def iprintanywhere_login(path, username, passwd):
    """
    Logs into iprintanywhere.buffalo.edu. Used to submit printing jobs.
    """

    driver = webdriver.Chrome(path)
    driver.implicitly_wait(5)
    driver.get('https://iprintanywhere.buffalo.edu/cps/Login')

    driver.find_element_by_name('principal').send_keys(username)
    driver.find_element_by_name('credentials').send_keys(passwd)
    driver.find_element_by_name('Submit').click()

    return driver

def myiprint_login(driver, username, passwd):
    """
    Logs into myprint.buffalo.edu. This site releases jobs to UB printers.
    """

    driver.get('https://myiprint.buffalo.edu:7773/user/signin.jsp')

    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').send_keys(passwd)
    driver.find_element_by_name('sign_in').click()

    return driver

def chose_printer(driver, printer):
    """
    Chose printer to print to.
    """

    #Ensure that login went through successfully and if not, close and exit
    try:
        driver.find_element_by_partial_link_text(printer).click();
    except:
        print('Login Failed')
        driver.close()
        exit(1)

    return driver

def send_document(driver, filepath, ubit):
    """
    Sends documents that are uploaded and ready to be released.
    """
    driver.find_element_by_class_name('fileUpload').send_keys(filepath)
    driver.find_element_by_id('clientUID').send_keys(ubit)

    driver.find_element_by_name('Submit').click()
    driver.find_element_by_name('Submit').click()

    try:
        driver.switch_to.frame(driver.find_element_by_xpath(xpath="//iframe[1]"))
        #Need to sleep for 2 seconds to avoid throwing exception, selenium runs behind
        sleep(2)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='glyphicons x3 green glyphicons-ok']")))
        driver.switch_to_default_content()
    except TimeoutException:
        print("Loading took too much time!")

    return driver

def release_prints(driver):
    """
    Releases every print that has been submitted and pays for them.
    """

    for ele in driver.find_elements_by_name('print_job'):
        ele.click()

    driver.find_element_by_id('payPrintButton').click()

    return driver

def main():

    parser = argparse.ArgumentParser(description='A small script that helps automate printing on personal computers to UB printers')

    parser.add_argument('-u', '--user', required=True, help='UBIT to log into printing sites', type=str)
    parser.add_argument('-p', '--passwd', required=True, help='Password associated with your UBIT', type=str)
    parser.add_argument('-l', '--location', required=True,
                        help='Chose a location to print. Current valid locations are: Capen/Capen-color, or Lockwood/Lockwood-color',
                        choices=['Capen', 'Capen-color', 'Lockwood', 'Lockwood-color'])
    parser.add_argument('-f', '--filepaths', required=True, help='Paths to file or files that will be printed', nargs='+')
    parser.add_argument('-c', '--chromedriver-path', help='Path to chrome webdriver')

    args = parser.parse_args()

    ubit = args.user
    passwd = args.passwd
    filepaths = args.filepaths
    printer_loc = args.location
    chromedriver_path = args.chromedriver_path

    # Log in to iprintanywhere, throw exception if login failed
    driver = iprintanywhere_login(chromedriver_path, ubit, passwd)

    # if driver.find_element_by_class_name('alert.alert-danger.messages')

    for fp in filepaths:
        driver = chose_printer(driver, printer_loc)
        driver = send_document(driver, fp, ubit)

    driver = myiprint_login(driver, ubit, passwd)

    driver = release_prints(driver)

    driver.close()
