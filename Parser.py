import csv
from typing import TextIO


def parse_txt_file(file: TextIO):
    x_arr = []
    y_arr = []
    s = file.readline()
    while s != '':
        try:
            x, y = map(float, s.split())
            x_arr.append(x)
            y_arr.append(y)
        except ValueError:
            print(f'wrong input: {s}')
        s = file.readline()

    return x_arr, y_arr


def parse_csv_file(file: TextIO):
    x_arr = []
    y_arr = []
    spamreader = csv.reader(file, delimiter=',', quotechar='"')
    for row in spamreader:
        try:
            x, y = map(lambda item: float(item.replace(",", ".")), row)
            x_arr.append(x)
            y_arr.append(y)
        except ValueError:
            print(f'wrong input: {row}')

    return x_arr, y_arr
