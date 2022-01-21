import pandas as pd

data = pd.read_excel(
    r"C:\Users\sob09\Downloads\daftar-kabupaten-kota-di-indonesia-excel.xlsx")
dj = data.to_json

print(dj)
