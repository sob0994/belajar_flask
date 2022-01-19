import pandas as pd

df = pd.read_json(r"D:\webapp\python\ksp-py\app\Data\Prov.json")
df.to_csv(r"D:\webapp\python\ksp-py\app\Data\Prov.csv", index=None)
# df.to_excel(r"D:\webapp\python\ksp-py\app\Data\Prov.csv", index=None)