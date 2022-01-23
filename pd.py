from sqlite3 import converters
from numpy import dtype
import pandas as pd

# data = pd.read_excel(
#     r"C:\Users\sob09\Downloads\daftar-kabupaten-kota-di-indonesia-excel.xlsx")
# dj = data.to_json

# print(dj)

flJson = pd.read_json(
    r'D:\webapp\python\ksp-py\app\Data\Kota.json', dtype={'Kode', str})
flJson.to_csv(r'D:\webapp\python\ksp-py\app\Data\Kota.csv', index=0)
