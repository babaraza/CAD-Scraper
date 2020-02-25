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
    parameters = {'ty': 2019, 'f': address}

    # The FBCAD URL for the initial query
    url = 'https://fbcad.org/ProxyT/Search/Properties/quick'

    s = r.get(url, headers=headers, params=parameters)

    # Check for errors
    s.raise_for_status()

    # The returned data is in JSON format so parsing JSON
    json_data = json.loads(s.text)

    # In the JSON results, Record Count shows 0 if property not found
    if json_data['RecordCount'] != 0:
        # If property is found, retrieve the property IDs
        # and call get_data()
        id_one = json_data['ResultList'][0]['PropertyQuickRefID']
        id_two = json_data['ResultList'][0]['PartyQuickRefID']
        return get_data(id_one, id_two)
    else:
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
    parameters = {'PropertyQuickRefID': id_one, 'PartyQuickRefID': id_two}
    url = 'https://fbcad.org/Property-Detail'

    s = r.get(url, headers=headers, params=parameters)

    # Parsing results from above url through BeautifulSoup
    soup = BeautifulSoup(s.text, 'lxml')

    # The property page on FBCAD is made up for tables
    # Getting the first set of data we need which is in a <td>
    header_data = soup.find_all('td', class_='propertyData')

    # Getting the Account # / Property ID
    acct_number = header_data[0].text

    # The complete address for the house
    formatted_address = header_data[2].text

    # The appraised value for the house
    appraised_value = header_data[3].text

    # The square footage for the house
    square_foot = soup.find_all(class_='improvementsFieldData')[3].text

    # Element labels: Main Area, Attached Garage, Open Porch etc
    house_elements_labels = soup.find_all(class_='segmentTableColumn2')

    # Skipping the first cell of labels as it is the table header
    element_labels = [item.text for item in house_elements_labels[1:]]

    # Element values for each of the labels above
    house_elements_values = soup.find_all(class_='segmentTableColumn4')

    # Skipping the first cell of values as it is the table header
    # Also removing the ',' from the values to allow conversion to int
    element_values = [item.text.replace(',', '').replace('-', '0') for item in house_elements_values[1:]]

    # Adding the FBCAD Account Number to the element arrays
    element_labels.append("Acct #")
    element_values.append(acct_number)

    # Creating a tuple from the element labels and element values
    elements = tuple(zip(element_labels, element_values))

    # Setting the default value for these variables to 0
    porch, patio, deck, garage = [0] * 4
    stories = 1

    # Iterating over the tuple called elements of key/value pairs to extract data
    for k, v in elements:
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
        year_built = soup.find_all(class_='segmentTableColumn3')[1].text
    except AttributeError:
        year_built = "Not Found"

    # Sub-elements: Bedrooms, Baths, Heat and AC etc
    # Creating empty list to hold the sub_elements
    sub_elements = []

    # Selecting the table that has the sub_elements
    sub_elements_table = soup.find('table', class_='segmentDetailsTable')

    # Getting all the rows inside the sub_elements table
    sub_elements_table_rows = sub_elements_table.find_all('tr')

    # Iterating over each row
    for row in sub_elements_table_rows:
        # Getting all cells in each row
        cells = row.find_all('td')
        # The sub_elements section has six columns of data
        # We only need the middle two columns
        for cell in cells[2:4]:
            # Adding the sub_elements labels and values to the sub_elements list
            sub_elements.append(cell.text)

    # Getting the number of bedrooms, bathrooms, and fireplace
    bedrooms = sub_elements[1]
    baths = float(str(sub_elements[3])[:3])
    fireplace = sub_elements[7]

    # Selecting the Sales History table to get last sale information
    # Finding the element that has SALES HISTORY text and then selecting
    # it's parent and then it's parent
    sales_table_raw = soup.find(class_='sectionHeader', string='SALES HISTORY').parent.parent

    # Selecting the first table inside the selection above
    sales_table = sales_table_raw.find('table')

    # Getting all the rows <tr>
    sales_table_rows = sales_table.find_all('tr')

    # Getting the first row of data which includes deed date, seller, buyer etc
    sales_data = sales_table_rows[1].text.strip().split('\n')

    # Extracting the Purchase Date
    try:
        purchase_date = sales_data[0]
    except:
        purchase_date = "Not Found"

    # Extracting the name of the buyer
    try:
        buyer = sales_data[2]
    except:
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
                    bedrooms=bedrooms,
                    baths=baths,
                    fireplace=fireplace,
                    stories=stories,
                    elements=elements)

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
