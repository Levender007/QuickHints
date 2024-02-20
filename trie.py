import datrie  # Библиотеки
import string
import os.path
import pandas
from textblob import TextBlob

from WWH import checkHash, getFileHash  # Мои файлы

import json  # Debug tools
import time


class PrefTrie:
    def __init__(self, config: dict):
        self.conf = config
        self.trieStatus = 0  # Статус готовности префиксного дерева. -1/0/1 – ошибка инициализации/изменяется/готово
        self.trie = datrie.Trie(string.ascii_lowercase + string.digits + string.punctuation + string.whitespace)  # Префиксное дерево

        print("Инициализация префиксного дерева запросов")

        if os.path.isfile(self.conf['triePath']):  # Поиск файла сохранения
            self.load()
        else:
            self.build()

        print("Инициализация дерева завершена")

    def build(self):  # Создание дерева
        self.trieStatus = 0
        print("Построение дерева")

        try:
            buildSet = pandas.read_csv(self.conf['dataset'], encoding="ISO-8859-1", usecols=["product_uid", "search_term", "relevance"])
        except Exception:
            print("Нет доступа к dataset-файлу")
            self.trieStatus = -1
            return
        i = 0
        for row in buildSet.iloc:
            corSearch = str(TextBlob(row['search_term'].lower()).correct())  # Исправление ошибок
            if corSearch not in self.trie:  # Добавление нового запроса
                self.trie[corSearch] = [0.0, 0, self.conf["minHarTovRelevance"]]  # Популярность запроса. UID характерного товара. Релевантность характерного товара
            if row['relevance'] >= self.conf['minRelevance']:  # Модификация старого запроса
                self.trie[corSearch][0] += row['relevance'] - 1
            if row['relevance'] > self.trie[corSearch][2]:
                self.trie[corSearch][1] = row['product_uid']
                self.trie[corSearch][2] = row['relevance']
            i += 1
            print(i, "строк обработанно")
        self.trieStatus = 1
        self.save()

        print("Построение дерева завершено")

    def getNWords(self, prefix, n):  # n – максимальное кол-во результатов
        if self.trieStatus != 1:
            print("Невозможно найти ключи: Дерево в процессе изменения параметров")
            return 0
        res = []
        i = 0
        state = datrie.State(self.trie)
        state.walk(prefix)
        it = datrie.Iterator(state)
        while it.next() and i < n:
            i += 1
            res.append(tuple([prefix + it.key(), it.data()]))
        return res

    def getWords(self, prefix):  # Поиск всех запросов с данным префиксом
        if self.trieStatus != 1:
            print("Невозможно найти ключи: Дерево в процессе изменения параметров")
            return 0
        return self.trie.items(prefix)

    def load(self):  # Загрузка дерева
        self.trieStatus = 0
        print("Загрузка дерева")

        try:  # Получение сохранённого хэша
            with open(self.conf['hashFile'], 'r') as file:
                self.conf['savefileHash'] = file.read()
        except Exception:
            x = input("Нет доступа к hash-файлу. Загрузить дерево без проверки hash-суммы? (Y/N)\t").lower()
            if x == 'y':
                self.trie = datrie.Trie.load(self.conf['triePath'])
                self.trieStatus = 1
                return
            else:
                self.conf['savefileHash'] = -1

        if checkHash(self.conf['triePath'], self.conf['savefileHash']):  # Проверка файла сохранения
            self.trie = datrie.Trie.load(self.conf['triePath'])
            self.trieStatus = 1
        else:
            x = input("Hash файла сохранения префиксного дерева не совпадает с сохранённым значением. Перестроить дерево? (Y/N)\t").lower()
            if x == 'y':
                self.build()
            else:
                self.trieStatus = -1

    def save(self):
        if self.trieStatus != 1:
            print("Невозможно сохранить дерево: Дерево в процессе изменения параметров")
            return
        self.trieStatus = 0
        print("Сохранение префиксного дерева")

        try:
            self.trie.save(self.conf['triePath'])
        except Exception:
            print("Ошибка сохранения префиксного дерева")
            return

        x = getFileHash(self.conf['triePath'])
        if x == -1:
            print("Ошибка расчёта хэша файла")
            return 

        try:
            with open(self.conf['hashFile'], 'w') as file:
                file.write(x)
        except OSError:
            print("Ошибка сохранения хэша файла")

        self.trieStatus = 0
        print("Сохранение завершено")

    def update(self, name, value):
        if self.trieStatus != 1:
            print("Невозможно обновить дерево: Дерево в процессе изменения параметров")
            return
        self.trieStatus = 0

        corSearch = str(TextBlob(name.lower()).correct())
        if corSearch not in self.trie:
            self.trie[corSearch] = [0.0, 0, self.conf["minHarTovRelevance"]]  # Популярность запроса. UID характерного товара. Релевантность характерного товара
        if value['relevance'] >= self.conf['minRelevance']:
            self.trie[corSearch][0] += value['relevance'] - 1
        if value['relevance'] > self.trie[corSearch][2]:
            self.trie[corSearch][1] = value['product_uid']
            self.trie[corSearch][2] = value['relevance']

        self.trieStatus = 1


if __name__ == "__main__":
    print("Debug mode")
    file = open('./configs/trieConfig.json')
    trie = PrefTrie(json.load(file))
    start = time.time_ns()
    trie.getWords('b')
    print(- start + time.time_ns())
    start = time.time_ns()
    trie.getNWords('b', 10)
    print(- start + time.time_ns())
    file.close()
