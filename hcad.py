from bs4 import BeautifulSoup
import pyperclip
import requests

# Got help from https://stackoverflow.com/questions/45654298/cant-parse-name-from-a-webpage-using-post-request
# for using referer in the post call


def get_data(stnum, stname):
    # Creating a new request session
    r = requests.Session()

    # Setting User agent to mimic browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
               'Content-type': 'application/x-www-form-urlencoded',
               'Referer': 'https://public.hcad.org/records/quicksearch.asp'}

    # The HCAD URL for the initial query
    url = 'https://public.hcad.org/records/QuickRecord.asp'

    # These are the params for the POST call to HCAD url
    payload = {'TaxYear': '2019',
               'stnum': stnum,
               'stname': stname}

    s = r.post(url, headers=headers, data=payload)

    # Check for errors
    s.raise_for_status()

    print(s.text)


get_data(stnum='', stname='')
