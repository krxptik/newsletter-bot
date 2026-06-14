import re

def clean_ordinal_day(date_str):
    # converts '5th January 2026' -> '5 January 2026'
    return re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', date_str)