# ================================================================
# path: tuutrag/scrapers.py
# brief: tuutrag module exports
# ================================================================
from exports import export

from .paths import DIR_DATA_SCRAPED
@export
def ccsds_scraper():
    """Scrapes books [Blue, Magenta] from www.ccsds.org/publications/[color]books"""
    save_dir = DIR_DATA_SCRAPED
    book_colors = ["blue", "magenta"]

    

    
