from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyperclip

app = Flask(__name__)

BASE_URL = 'https://daisyui.com/components/'


@app.route('/scrape', methods=['GET'])
def handle_request():
    component_name = request.args.get('component')
    if component_name is None:
        return jsonify({'error': 'Missing component parameter'}), 400

    try:
        return scrape_docs(component_name)
    except Exception as e:
        return jsonify({'error': e}), 500


def scrape_docs(component):
    url = f'{BASE_URL}{component}'
    driver = webdriver.Chrome()
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.TAG_NAME, "table")))

    component_dict = {}
    component_dict['table'] = get_component_table(driver)
    component_dict['examples'] = get_component_examples(driver)

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        driver.close()

    return component_dict


def get_component_table(driver):
    component_table = driver.find_element(By.TAG_NAME, 'table')
    component_table_soup = BeautifulSoup(
        component_table.get_attribute('outerHTML'), 'html.parser')
    return component_table_soup.prettify()


def get_component_examples(driver):
    examples_dict = {}

    component_examples = driver.find_elements(By.CSS_SELECTOR,
                                              ".component-preview")
    for example in component_examples:
        example_tabs = example.find_element(
            By.CLASS_NAME, 'tabs').find_elements(By.TAG_NAME, "button")
        jsx_tab = example_tabs[-1]
        driver.execute_script("arguments[0].scrollIntoView();", jsx_tab)
        time.sleep(.5)
        jsx_tab.click()

        copy_button = example.find_element(
            By.CSS_SELECTOR, "[data-tip='copy']")
        copy_button.click()

        code_example = pyperclip.paste()

        component_id = example.get_attribute('id')
        examples_dict[component_id] = code_example

    return examples_dict


if __name__ == '__main__':
    app.run(port=5000, debug=True)
