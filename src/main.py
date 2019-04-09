from scraper import WebScraper
import pandas as pd

# Indicar el curs a capturar entre 1314 i 1819. "ALL" per a tots.
course = "1819"

ws = WebScraper(course)

ws.scrape()
ws.write_csv()

pd.set_option('display.max_columns', None)
print(ws.get_data())
