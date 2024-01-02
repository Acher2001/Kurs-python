from flask import Flask, request, Response
import json

app = Flask(__name__)

# Инициализация данных о валютах и курсах
currencies = {'usd': 1, 'rub': 65.5, 'eur': 73.4}
amounts = {'usd': 200, 'rub': 100, 'eur': 300}

# GET запросы
@app.route('/usd/get', methods=['GET'])
def get_usd():
    return str(amounts['usd'])

@app.route('/rub/get', methods=['GET'])
def get_rub():
    return str(amounts['rub'])

@app.route('/eur/get', methods=['GET'])
def get_eur():
    return str(amounts['eur'])

@app.route('/amount/get', methods=['GET'])
def get_amount():
    rub_usd_rate = currencies['rub'] / currencies['usd']
    rub_eur_rate = currencies['rub'] / currencies['eur']
    usd_eur_rate = currencies['usd'] / currencies['eur']

    response = f"rub: {amounts['rub']}\nusd: {amounts['usd']}\neur: {amounts['eur']}\n"
    response += f"rub-usd: {rub_usd_rate:.2f}\nrub-eur: {rub_eur_rate:.2f}\nusd-eur: {usd_eur_rate:.2f}\n"
    response += f"sum: {amounts['rub'] * currencies['rub']:.2f} rub / {amounts['usd'] * currencies['usd']:.2f} usd / {amounts['eur'] * currencies['eur']:.2f} eur"

    return Response(response, headers={'content-type': 'text/plain'})

# POST запросы
@app.route('/amount/set', methods=['POST'])
def set_amount():
    data = request.json
    for currency, value in data.items():
        amounts[currency] = value
    return "Amounts updated successfully"

@app.route('/modify', methods=['POST'])
def modify_amount():
    data = request.json
    for currency, value in data.items():
        amounts[currency] += value
    return "Amounts modified successfully"

if __name__ == '__main__':
    app.run(port=8080, threaded=True)
