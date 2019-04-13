from scraper import WebScraper

# Indicar el curs a capturar entre 1314 i 1819. "ALL" per a tots.
course = "1314"

ws = WebScraper(course)

ws.scrape()
ws.write_csv()

