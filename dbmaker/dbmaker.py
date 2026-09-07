import pandas as pd

url = "https://cartup.com/?srsltid=AfmBOoo_7_HNHfI_VBljIpZs13J2lgks6KGXlDkdGAi2YvvpTVNya6jZ"

tables = pd.read_html(url)

df = tables[0]

print(df)

df.to_csv("cartup.csv", index=False)