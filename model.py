from flask import current_app, redirect, render_template, url_for

from time import time_ns  # Debug tools


def main_menu(method, form):
    if method == 'GET':
        return render_template('main_menu.html')
    else:
        if form['code'] == "0":
            current_app.config['trie'].build()
        elif form['code'] == "1":
            current_app.config['trie'].save()
        elif form['code'] == "2":
            current_app.config['brandTable'].build()
        else:
            current_app.config['brandTable'].save()
        return redirect(url_for('menu'))


def hint_model(method, form):
    if method == 'GET':
        return 'hint_in.html', []
    else:
        start_time = time_ns()  # Debug
        res = current_app.config['trie'].getWords(form['search'])
        if res == 0:
            return 'busy.html', []

        def key(x):
            return x[1][0]

        res.sort(key=key)
        res = res[:current_app.config['maxHintCount']]

        res2 = []
        for item in res:
            brand = current_app.config['brandTable'].getBrandFromPID(item[1][1])
            res2.append([item[0], brand])
        end_time = time_ns()  # Debug
        print("Hint generation time:", int((end_time - start_time) / pow(10, 6)), "ms")  # Debug
        return 'hint_out.html', res2


def trie_update(method, form):
    if method == 'GET':
        return render_template('trie_in.html')
    else:
        current_app.config['trie'].update(form['search'], {"relevance": float(form['relevance']), 'product_uid': int(form['pid'])})
        return redirect(url_for('menu'))


def brand_update(method, form):
    if method == 'GET':
        return render_template('brand_in.html')
    else:
        current_app.config['brandTable'].update(int(form['pid']), form['brand'])
        return redirect(url_for('menu'))
