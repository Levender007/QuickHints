from os import path  # Библиотеки
import pandas

import json  # Debug tools
from time import time_ns


class BrandTable:
    def __init__(self, config: dict):
        self.conf = config
        self.table = pandas.Series(-1)

        print("Инициализация таблицы брендов")

        if path.isfile(self.conf['tablePath']):
            self.load()
        else:
            self.build()

        print("Инициализация таблицы завершена")

    def build(self):
        print("Построение таблицы брендов")

        try:
            attr = pandas.read_csv(self.conf['dataset'], encoding="ISO-8859-1")
        except Exception:
            print("Ошибка получения доступа к файлу датасета")
            return

        pid = []
        brand = []
        i = 0
        for row in attr.iloc:
            if row['name'] == "MFG Brand Name":
                pid.append(int(row["product_uid"]))
                brand.append(row["value"])
            i += 1
            print(i, "строк обработано")
        self.table = pandas.Series(brand, index=pid)

        print("Построение таблицы завершено")
        self.save()

    def getBrandFromPID(self, pid):  # pid – product ID
        if pid in self.table:
            return self.table[pid]
        else:
            return -1

    def load(self):
        print("Загрузка таблицы брендов")

        try:
            save = pandas.read_csv(self.conf['tablePath'])
            self.table = pandas.Series(save.iloc[:, 1])
            self.table.index = save.iloc[:, 0]

            print("Загрузка таблицы завершена")
        except Exception:
            x = input("Ошибка загрузки таблицы брендов. Перестроить таблицу? (Y/N)\t").lower()
            if x == 'y':
                self.build()

    def save(self):
        print("Сохранение таблицы брендов")
        try:
            self.table.to_csv(self.conf['tablePath'])

            print("Сохранение завершено")
        except Exception:
            print("Ошибка сохранения таблицы брендов")

    def update(self, pid, brandName):  # pid – product ID
        self.table[pid] = brandName


if __name__ == "__main__":
    print("Debug mode")
    file = open("./configs/brandTableConfig.json")
    test = BrandTable(json.load(file))
    file.close()
    test.update(10, "test")
    print(test.table[10])
    start = time_ns()
    test.getBrandFromPID(179042)
    print(time_ns() - start)
    print("Total names:", len(test.table))
