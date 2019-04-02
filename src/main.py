from scraper import WebScraper
from pandas import DataFrame
import os

ws = WebScraper()

# Indicar el curs a capturar entre 1314 i 1819
course = "1314"

outname = "dades" + course + ".csv"

outdir = '../data'
if not os.path.exists(outdir):
    os.mkdir(outdir)
course_file = os.path.join(outdir, outname)    

df = ws.scrape(course)
df.to_csv(course_file, index=False,header=True,sep=';')
