from utilities import House, format_result
from bs4 import BeautifulSoup
import pyperclip
import requests
import json


def get_property_id(address):
    """
    This function queries the FBCAD website for the unique Property ID
    and Quick Reference ID assigned by FBCAD.

    If the property is not found this function returns None.

    :param address: User provided address to search on FBCAD website
    :return: FBCAD Property ID and Quick Reference ID or None
    """

    # Creating a new request session
    r = requests.Session()

    # Setting User agent to mimic browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}

    # These are the params for the GET call to FBCAD url
    # parameters = {'ty': 2020, 'f': address}
    parameters = {'keywords': address}

    # The FBCAD URL for the initial query
    url = 'https://esearch.fbcad.org/Search/SearchResults'

    try:
        s = r.get(url, headers=headers, params=parameters)

        # Check for errors
        s.raise_for_status()

        # The returned data is in JSON format so parsing JSON
        json_data = json.loads(s.text)

        # In the JSON results, Record Count shows 0 if property not found
        if json_data['TotalResults'] != 0:
            # If property is found, retrieve the property IDs
            # and call get_data()
            id_one = json_data['ResultsList'][0]['PropertyId']
            id_two = json_data['ResultsList'][0]['DetailUrl']
            return get_data(id_one, id_two)
        else:
            return None

    except requests.exceptions.HTTPError as e:
        print(e)
        return None


def get_data(id_one, id_two):
    """
    Gets all the data from the FBCAD website for the particular property.

    :param id_one: FBCAD Property ID
    :param id_two: FBCAD Quick Reference ID
    :return: An instance of the House object containing the results
    """

    # Creating a new request session
    r = requests.Session()

    # Setting User agent to mimic browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}

    # These are the params for the specific property
    url = 'https://esearch.fbcad.org' + id_two

    s = r.get(url, headers=headers)

    # Parsing results from above url through BeautifulSoup
    soup = BeautifulSoup(s.text, 'lxml')

    # The property page on FBCAD is made up of tables
    tables = soup.find_all('div', class_="table-responsive")

    house_elements_table = tables[1]
    house_value_table = tables[3]
    house_deed_table = tables[-1]

    # The complete address for the house
    formatted_address = soup.find('th', text='Address:').next_element.next_element.text

    # The appraised value for the house
    house_value_rows = house_value_table.find_all('tr')[1:3]
    for row in house_value_rows:
        cells = row.find_all('td')
        if cells[-1].text != "N/A":
            appraised_value = cells[-1].text

    # The square footage for the house
    sqft_raw = house_elements_table.find('div', class_="panel-table-info").find_all('span')[-1].text.split()[2]
    square_foot = sqft_raw.replace('sqft', '')[:-3]

    # Elements: Main Area, Attached Garage, Open Porch etc
    house_elements_table_rows = house_elements_table.find_all('tr')

    house_elements = []

    # Getting the Account # / Property ID
    acct_number = id_one
    # Adding the FBCAD Account Number to the element arrays
    house_elements.append(["Acct #", acct_number])

    # Skipping the first cell of values as it is the table header
    for row in house_elements_table_rows[1:]:
        cells = row.find_all('td')
        house_elements.append([cells[1].text.strip(), cells[-2].text.replace('.00', '').strip()])

    # Setting the default value for these variables to 0
    porch, patio, deck, garage = [0] * 4
    stories = 1

    # Iterating over the tuple called elements of key/value pairs to extract data
    for k, v in house_elements:
        # If the word Porch/Patio appears in the element label above (k)
        # then add its value (v) to the variable porch/patio
        if 'Porch' in k:
            porch += int(v)
        if 'Patio' in k:
            patio += int(v)
        if 'Deck' in k:
            deck += int(v)
        if 'Garage' in k:
            garage += int(v)
        if 'Story' in k:
            stories = 2

    # Get the year built
    try:
        year_built = house_elements_table_rows[1].find_all('td')[-3].text
    except AttributeError:
        year_built = "Not Found"

    # Selecting the Deed History table to get last sale information
    # Getting the first row of data which includes deed date, seller, buyer etc
    house_deed_rows = house_deed_table.find_all('tr')[1:2]
    for row in house_deed_rows:
        cells = row.find_all('td')
        # Extracting the Purchase Date
        try:
            purchase_date = cells[0].text
        except None:
            purchase_date = "Not Found"
        # Extracting the name of the buyer
        try:
            buyer = cells[4].text
        except None:
            buyer = "Not Found"

    # Creating a House instance with the above scraped data
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
                    bedrooms='',
                    baths='',
                    fireplace='',
                    stories=stories,
                    elements=house_elements)

    # Return the House object
    return results


if __name__ == '__main__':
    # Ask the user for the address to search
    query = input("Enter Property Address > ")

    # Running a search on the address
    result = get_property_id(query.strip())

    # Checking if the property was found
    if result:
        pyperclip.copy(format_result(result))
    else:
        print("Property Not Found")
        pyperclip.copy("Property Not Found")
