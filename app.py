from flask import Flask, render_template, request  # Библиотеки
import json

from brand_table import BrandTable  # Мои файлы
from model import *
from trie import PrefTrie


app = Flask(__name__)
with open('./configs/appConfig.json') as file:
    x = json.load(file)
    app.config["trieConf"] = x["trieConf"]
    app.config["brandTableConf"] = x["brandTableConf"]
    app.config["maxHintCount"] = x["maxHintCount"]


@app.route("/", methods=['GET', 'POST'])
def menu():
    html = main_menu(request.method, request.form)
    return html


@app.route("/hint", methods=['GET', 'POST'])
def hint():
    html, args = hint_model(request.method, request.form)
    return render_template(html, args=args)


@app.route("/trie", methods=['GET', 'POST'])
def trie():
    html = trie_update(request.method, request.form)
    return html


@app.route("/brand", methods=['GET', 'POST'])
def brand():
    html = brand_update(request.method, request.form)
    return html


if __name__ == '__main__':
    flag = 1
    try:
        with open(app.config["trieConf"]) as file:
            trieConf = json.load(file)
        with open(app.config["brandTableConf"]) as file:
            brandConf = json.load(file)

        app.config['trie'] = PrefTrie(trieConf)
        app.config['brandTable'] = BrandTable(brandConf)
    except Exception:
        print("Ошибка конфигурации префиксного дерева и/или таблицы брендов")
        flag = 0

    if flag == 1 and app.config['trie'].trieStatus != -1:
        app.run(host='127.0.0.1', port=3000, debug=True)
    elif app.config['trie'].trieStatus == -1:
        print("Ошибка инициализации префиксного дерева")
