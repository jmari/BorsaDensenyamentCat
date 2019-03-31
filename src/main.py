from scraper import WebScraper

ws = WebScraper()

# Indicar el curs a capturar entre 1314 i 1819
course = "1718"
course_name = "../data/" + "dades" + course + ".csv"

df = ws.scrape(course)
df.to_csv(index=False)