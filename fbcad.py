from bs4 import BeautifulSoup
import pyperclip
import requests
import json


class House:
    def __init__(self, address, sqft, value, year_built, porch, patio, deck, garage, purchase_date, buyer, bedrooms,
                 baths, fireplace, elements):
        self.address = address
        self.sqft = sqft
        self.value = value
        self.year_built = year_built
        self.porch = porch
        self.patio = patio
        self.deck = deck
        self.garage = garage
        self.purchase_date = purchase_date
        self.buyer = buyer
        self.bedrooms = bedrooms
        self.baths = baths
        self.fireplace = fireplace
        self.elements = elements


def get_property_id(address):
    r = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}

    parameters = {'ty': 2019, 'f': address}

    url = 'https://fbcad.org/ProxyT/Search/Properties/quick'

    s = r.get(url, headers=headers, params=parameters)
    s.raise_for_status()

    json_data = json.loads(s.text)

    if json_data['RecordCount'] != 0:
        id_one = json_data['ResultList'][0]['PropertyQuickRefID']
        id_two = json_data['ResultList'][0]['PartyQuickRefID']
        return get_data(id_one, id_two)
    else:
        return "Property Not Found"


def get_data(id_one, id_two):
    r = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}

    parameters = {'PropertyQuickRefID': id_one, 'PartyQuickRefID': id_two}
    url = 'https://fbcad.org/Property-Detail'

    s = r.get(url, headers=headers, params=parameters)
    soup = BeautifulSoup(s.text, 'lxml')

    header_data = soup.find_all("td", class_="propertyData")
    formatted_address = header_data[2].text
    appraised_value = header_data[3].text
    square_foot = soup.find_all(class_='improvementsFieldData')[3].text

    # Element names: Main Area, Attached Garage, Open Porch etc
    house_elements_labels = soup.find_all(class_='segmentTableColumn2')
    element_names = [item.text for item in house_elements_labels[1:]]

    # Element Values
    house_elements_values = soup.find_all(class_='segmentTableColumn4')
    element_value = [int(item.text.replace(',', '')) for item in house_elements_values[1:]]

    elements = tuple(zip(element_names, element_value))

    porch, patio, deck, garage = [0] * 4

    for k, v in elements:
        if 'Porch' in k:
            porch += v
        if 'Patio' in k:
            patio += v
        if 'Deck' in k:
            deck += v
        if 'Garage' in k:
            garage += v

    try:
        year_built = soup.find_all(class_='segmentTableColumn3')[1].text
    except AttributeError:
        year_built = "Not Found"

    # Sub-elements: Bedrooms, Baths, Heat and AC etc
    subelements = []
    subelements_table = soup.find('table', class_="segmentDetailsTable")
    subelements_table_rows = subelements_table.find_all('tr')

    for row in subelements_table_rows:
        cells = row.find_all('td')
        for cell in cells[2:4]:
            subelements.append(cell.text)

    bedrooms = subelements[1]
    baths = float(str(subelements[3])[:3])
    fireplace = subelements[7]

    sales_data_headers = ['Deed Date', 'Seller', 'Buyer', 'Instrument']
    sales_table_raw = soup.find(class_='sectionHeader', string='SALES HISTORY').parent.parent
    sales_table = sales_table_raw.find('table')
    sales_table_rows = sales_table.find_all('tr')
    sales_data_values = sales_table_rows[1].text.strip().split('\n')

    sales_data = list(zip(sales_data_headers, sales_data_values))

    try:
        purchase_date = sales_data[0][1]
    except:
        purchase_date = "Not Found"

    try:
        buyer = sales_data[2][1]
    except:
        buyer = "Not Found"

    results = House(address=formatted_address,
                    sqft=square_foot,
                    value=appraised_value,
                    year_built=year_built,
                    porch=porch,
                    patio=patio,
                    deck=deck,
                    garage=garage,
                    purchase_date=purchase_date,
                    buyer=buyer,
                    bedrooms=bedrooms,
                    baths=baths,
                    fireplace=fireplace,
                    elements=elements)
    return results


def format_result(house):
    template = f"""
{house.address}

STORY      : 
YEAR BUILT : {house.year_built}
ROOF REPL  : 
SQ FOOT    : {house.sqft}
BATHROOMS  : {house.baths}
GARAGE     : {house.garage}
FIREPLACE  : {house.fireplace}
OPEN PORCH : {house.porch}
PATIO      : {house.patio}
DOGS       : 
PAY        : 
EXTERIOR   : 
BOUGHT     : {house.purchase_date}
MARKET VAL : {house.value}
FLOOD QUOTE: 

{vars(house)}
"""
    return template


query = input("Enter Property Address > ")
result = get_property_id(query.strip())

if isinstance(result, str):
    pyperclip.copy("Property Not Found")
else:
    pyperclip.copy(format_result(result))
