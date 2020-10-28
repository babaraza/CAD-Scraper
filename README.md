[![Python 3.8](https://img.shields.io/badge/Python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

# County Appraisal District Scraper
Script to scrape property data from the County Appraisal District websites for Harris County and Fort Bend County

### Usage

Script can be run in Python Shell or CMD/Terminal by calling `app.py`



**Script has a CLI (command line interface):**

User will be first prompted to choose a county:

`(1) FBCAD or (2) HCAD >`

> *User can enter `x` at any point to go back to the previous input*



User will then be prompted to enter address for look up:

`Enter Property Address >`



###### If property is found:

- Script will copy the formatted data to clipboard
- This can be viewed by `CTRL+V` into any text editor



###### If property is not found:

- Script will return `Property Not Found`