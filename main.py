from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route('/scrape', methods=['GET'])
def scrape():
    component = request.args.get('component')
    if component is None:
        return jsonify({'error': 'Missing component parameter'}), 400

    url = f'https://daisyui.com/components/{component}'
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Unable to retrieve component docs'}), 500

    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table').prettify()

    component_dict = {}
    component_dict['table'] = table
    component_dict['examples'] = {}

    examples = soup.find_all('div', {'class': 'component-preview'})
    for component in examples:
        component_id = component.get('id')
        component_dict['examples'][component_id] = component.prettify()

    return component_dict


if __name__ == '__main__':
    app.run(port=5000, debug=True)
