from utilities import House, format_result
from bs4 import BeautifulSoup
import pyperclip
import requests
import re


def get_data(stnum, stname):
    """
    Goes to the HCAD website and searches the inputted address
    If found, scrapes all the data and returns an House object

    :param stnum: User inputted street number
    :param stname: User inputted street name
    :return: An instance of the House object containing all scraped data
    """

    # Creating a new request session
    r = requests.Session()

    # Setting User agent to mimic browser
    # Adding the referrer/content-type in the headers was the key to get this working
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
               'Content-type': 'application/x-www-form-urlencoded',
               'Referer': 'https://public.hcad.org/records/quicksearch.asp'}

    # The HCAD URL for the initial query
    url = 'https://public.hcad.org/records/QuickRecord.asp'

    # These are the params for the POST call to HCAD url
    payload = {'TaxYear': '2019',
               'stnum': stnum,  # This is the street number
               'stname': stname}  # This is the street name

    s = r.post(url, headers=headers, data=payload)

    # Check for errors
    s.raise_for_status()

    # Parsing the date into BeautifulSoup
    soup = BeautifulSoup(s.text, 'lxml')

    # Getting the latest appraised value
    # Since the table containing the value doesnt have an ID etc
    # I am selecting the cell with the text "Value as of..." then finding its parent table
    value_table = soup.find('td', string=re.compile("^Value as of")).parent.parent
    # Getting the second last row in the above table
    value_rows = value_table.find_all('tr')[-2]
    # Getting all the cells in the above table
    value_cells = value_rows.find_all('td')
    # Extracting the appraised value
    value = value_cells[-1].text.strip()

    # Getting the year built and sqft by finding the parent table
    year_table = soup.find('th', string="Year Built").parent.parent
    # Getting the second last row
    year_rows = year_table.find_all('tr')[-2]
    # Finding all the cells in the above table
    year_cells = year_rows.find_all('td')
    # Extracting the year built
    year_built = year_cells[1].text.strip()
    # Since the square foot is in the same table, getting sqft from same place
    sqft = year_cells[-2].text.strip()

    # Selecting the table on the bottom left of the HCAD page which has baths, fireplace etc
    building_data_table = soup.find('th', string='Building Data').parent.parent

    # Getting the half-baths
    try:
        # Selecting the cell, using regex, that has the words Half
        baths_half_cell = building_data_table.find('td', string=re.compile('(Half)')).parent
        baths_half = baths_half_cell.find_all('td')[-1].text
    except AttributeError:
        baths_half = 0

    # Getting the full-baths
    try:
        # Selecting the cell, using regex, that has the words Full
        baths_full_cell = building_data_table.find('td', string=re.compile('(Full)')).parent
        baths_full = baths_full_cell.find_all('td')[-1].text
    except AttributeError:
        baths_full = 0

    # Compiling the full and half baths so two and a half baths would be 2.5
    baths = int(baths_full) + int(baths_half) / 2

    # Getting the Fireplace
    try:
        # Selecting the cell, using regex, that has the words Fireplace
        fireplace_cell = building_data_table.find('td', string=re.compile('(Fireplace)')).parent
        fireplace = fireplace_cell.find_all('td')[-1].text
    except AttributeError:
        fireplace = 0

    # Selecting the table on the bottom right of the HCAD page which has porch, patio etc
    # Selecting the <th>, using regex, that has the words Building Areas
    building_area_table = soup.find('th', string=re.compile('(Building Areas)')).parent.parent
    # Getting all the data from the above table
    building_area_data = building_area_table.find_all('td')
    # Using list comprehension to extract labels and values from the above list separately
    building_area_labels = [label.text.title() for label in building_area_data[0::2]]
    building_area_values = [label.text for label in building_area_data[1::2]]

    # Some properties have Extra Features which show up on a separate table at the bottm
    # These can be detached garage, pool etc
    check_extra = soup.find('th', text="Extra Features")
    if check_extra:
        extra_table = check_extra.parent.parent
        extra_rows = extra_table.find_all('tr')[2:]
        for row in extra_rows[1:]:
            extra_cells = row.find_all('td')
            extra_raw = [cell.text for cell in extra_cells]
            # Appending the extra features labels/values to the lists created above
            building_area_labels.append(extra_raw[1].title())
            building_area_values.append(extra_raw[-2])
    else:
        pass

    # Getting HCAD Account Number from the page <title>
    # HCAD website has the account number as part of the <title> tag
    acct_number_data = soup.title.string
    # Getting the last item in the above string which is the acct number
    acct_number = acct_number_data.split()[-1]

    # Adding the HCAD Account Number to the building_area arrays
    building_area_labels.append("HCAD")
    building_area_values.append(acct_number)

    # Creating a tuple from the labels and values list created above to join them
    building_area = tuple(zip(building_area_labels, building_area_values))

    # Setting default values as 0
    porch, patio, deck, garage = [0] * 4

    # Setting default number of stories
    stories = 1

    # Going through each value in building_area to get total porch, patio etc
    for k, v in building_area:
        if 'porch' in k.lower():
            porch += int(v)
        if 'patio' in k.lower():
            patio += int(v)
        if 'deck' in k.lower():
            deck += int(v)
        if 'garage' in k.lower():
            garage += int(v)
        if 'upr' in k.lower():
            stories = 2

    # Getting the full formatted address
    address_row = soup.find('td', string="Property Address:").parent
    # The address in HCAD includes a <br\> so using ".contents" to create a list
    # that automatically splits the values
    address_raw = address_row.find('th').contents
    # In the above list, usually the first element will be street number and name
    # second element will be the <br\>
    # third element will be city, state, zip
    address = f'{address_raw[0]}, {address_raw[2]}'.strip()

    # Alternative method to get Address above
    # address_raw = str(address_row.find('th')).replace('<br/>', ', ').replace('</th>', '')
    # address = re.sub(r"<([^>]+)>", "", address_raw).strip()

    # Getting the Purchase date
    # To get date we have to click on Ownership History link that opens a popup
    # Finding and building the final Ownership History link
    ownership_url = "https://public.hcad.org" + soup.find('a', string="Ownership History")['href']

    # Going to the Ownership History link
    s2 = r.post(ownership_url, headers=headers)

    # Checking for errors
    try:
        s2.raise_for_status()

        # Parsing the date to BeautifulSoup
        soup2 = BeautifulSoup(s2.text, 'lxml')

        # Finding the table with the purchase date
        owner_table = soup2.find_all('table')[1]
        # Getting the cell that contains the text "Effective Date"
        effective_date = owner_table.find('td', text="Effective Date")
        # Moving to the next siblings to get the buyer name and purchase date
        buyer = effective_date.find_next('td').text
        purchase_date = effective_date.find_next('td').find_next('td').text

    except requests.exceptions.HTTPError as e:
        purchase_date = "Not found"
        buyer = "Not found"
        print(e)

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
                    buyer=buyer,
                    bedrooms='',
                    baths=baths,
                    fireplace=fireplace,
                    stories=stories,
                    elements=building_area)

    # Returning an instance of the House object with all the data
    return results


if __name__ == '__main__':
    # Ask the user for the address to search
    query = input("Enter Property Address > ")

    # Split the inputted address into street number and street name using regex
    # Find all the numbers at the start of the address
    street_number = re.findall(r'^[0-9]*', query)[0]
    # Find all the characters in the address that are not numbers
    street_name = re.findall(r'[^0-9]+', query)[0].strip()

    # Running a search on the address
    try:
        result = get_data(stnum=street_number, stname=street_name)
    except AttributeError:
        result = None

    # Checking if the property was found
    if result:
        pyperclip.copy(format_result(result))
    else:
        print("Property Not Found")
        pyperclip.copy("Property Not Found")
