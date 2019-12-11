from utilities import format_result
from counties import fbcad, hcad
import pyperclip
import re

selection = input('(1) FBCAD or (2) HCAD > ')

if selection == '1':
    # Ask the user for the address to search
    query = input("\nEnter FBCAD Property Address > ")

    # Running a search on the address
    result = fbcad.get_property_id(query.strip())

    # Checking if the property was found
    if result:
        pyperclip.copy(format_result(result))
    else:
        print("Property Not Found")
        pyperclip.copy("Property Not Found")

elif selection == '2':
    # Ask the user for the address to search
    query = input("\nEnter HCAD Property Address > ")

    # Split the inputted address into street number and street name using regex
    # Find all the numbers at the start of the address
    street_number = re.findall(r'^[0-9]*', query)[0]
    # Find all the characters in the address that are not numbers
    street_name = re.findall(r'[^0-9]+', query)[0].strip()

    # Running a search on the address
    try:
        result = hcad.get_data(stnum=street_number, stname=street_name)
    except AttributeError:
        result = None

    # Checking if the property was found
    if result:
        pyperclip.copy(format_result(result))
    else:
        print("Property Not Found")
        pyperclip.copy("Property Not Found")

else:
    print('Invalid input')
