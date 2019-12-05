from utilities import House, format_result
from bs4 import BeautifulSoup
import pyperclip
import requests
import re


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

    soup = BeautifulSoup(s.text, 'lxml')

    value_table = soup.find('td', string=re.compile("^Value as of")).parent.parent
    value_rows = value_table.find_all('tr')[-2]
    value_cells = value_rows.find_all('td')
    value = value_cells[-1].text.strip()

    year_table = soup.find('th', string="Year Built").parent.parent
    year_rows = year_table.find_all('tr')[-2]
    year_cells = year_rows.find_all('td')
    year_built = year_cells[1].text.strip()
    sqft = year_cells[-2].text.strip()

    building_data_table = soup.find('th', string='Building Data').parent.parent

    # Room: Half Bath 1
    try:
        baths_half_row = building_data_table.find('td', string=re.compile('(Half)')).parent
        baths_half = baths_half_row.find_all('td')[-1].text
    except AttributeError:
        baths_half = 0

    # Room: Full Bath 2
    try:
        baths_full_row = building_data_table.find('td', string=re.compile('(Full)')).parent
        baths_full = baths_full_row.find_all('td')[-1].text
    except AttributeError:
        baths_full = 0

    baths = int(baths_full) + int(baths_half) / 2

    # Fireplace: Masonry Firebrick 1
    try:
        fireplace_row = building_data_table.find('td', string=re.compile('(Fireplace)')).parent
        fireplace = fireplace_row.find_all('td')[-1].text
    except AttributeError:
        fireplace = 0

    # Building Areas all items 8
    building_area_table = soup.find('th', string=re.compile('(Building Areas)')).parent.parent
    building_area_data = building_area_table.find_all('td')
    building_area_labels = [label.text for label in building_area_data[0::2]]
    building_area_values = [label.text for label in building_area_data[1::2]]
    building_area = tuple(zip(building_area_labels, building_area_values))

    porch, patio, deck, garage = [0] * 4

    for k, v in building_area:
        if 'porch' in k.lower():
            porch += int(v)
        if 'patio' in k.lower():
            patio += int(v)
        if 'deck' in k.lower():
            deck += int(v)
        if 'garage' in k.lower():
            garage += int(v)

    address_row = soup.find('td', string="Property Address:").parent
    address_raw = address_row.find('th').contents
    address = f'{address_raw[0]}, {address_raw[2]}'.strip()

    # Alternative method to get Address
    # address_raw = str(address_row.find('th')).replace('<br/>', ', ').replace('</th>', '')
    # address = re.sub(r"<([^>]+)>", "", address_raw).strip()

    # Purchase date
    ownership_url = "https://public.hcad.org/" + soup.find('a', string="Ownership History")['href']

    s2 = r.post(ownership_url, headers=headers)
    s2.raise_for_status()

    soup2 = BeautifulSoup(s2.text, 'lxml')

    owner_table = soup2.find_all('table')[1]
    purchase_date = owner_table.find('td', text="Effective Date").find_next('td').find_next('td').text

    # Extra Features
    # Description: Frame Detached Garage Units: 484

    # Creating a House instance with the above scraped data
    results = House(address=address,
                    sqft=sqft,
                    value=value,
                    year_built=year_built,
                    porch=porch,
                    patio=patio,
                    deck=deck,
                    garage=garage,
                    purchase_date=purchase_date,
                    buyer='',
                    bedrooms='',
                    baths=baths,
                    fireplace=fireplace,
                    stories='',
                    elements=building_area)

    return results


# Ask the user for the address to search
query = input("Enter Property Address > ")

# Running a search on the address
result = get_data(stnum='', stname='')

# Checking if the property was found
if result:
    pyperclip.copy(format_result(result))
else:
    print("Property Not Found")
    pyperclip.copy("Property Not Found")
