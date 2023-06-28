from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyperclip

app = Flask(__name__)


@app.route('/scrape', methods=['GET'])
def scrape():
    example = request.args.get('component')
    if example is None:
        return jsonify({'error': 'Missing component parameter'}), 400

    url = f'https://daisyui.com/components/{example}'

    driver = webdriver.Chrome()
    driver.get(url)

    # Wait until at least one .component-preview is loaded
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located(
        (By.TAG_NAME, "table")))

    component_dict = {}

    component_table = driver.find_element(By.TAG_NAME, 'table')
    component_table_soup = BeautifulSoup(
        component_table.get_attribute('innerHTML'), 'html.parser')
    component_dict['table'] = component_table_soup.prettify()

    component_dict['examples'] = {}

    component_examples = driver.find_elements(By.CSS_SELECTOR,
                                              ".component-preview")
    for example in component_examples:
        example_tabs = example.find_element(
            By.CLASS_NAME, 'tabs').find_elements(By.TAG_NAME, "button")
        jsx_tab = example_tabs[-1]
        driver.execute_script("arguments[0].scrollIntoView();", jsx_tab)
        time.sleep(1)
        jsx_tab.click()

        copy_button = example.find_element(
            By.CSS_SELECTOR, "[data-tip='copy']")
        copy_button.click()

        code_example = pyperclip.paste()

        component_id = example.get_attribute('id')
        component_dict['examples'][component_id] = code_example

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        driver.close()

    return component_dict


if __name__ == '__main__':
    app.run(port=5000, debug=True)
