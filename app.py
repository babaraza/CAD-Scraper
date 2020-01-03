from utilities import format_result
from counties import fbcad, hcad
import pyperclip
import os
import re


def start_program():
    """
    Clears the command prompt screen
    Then initiates the program
    """

    # Clears the cmd screen
    os.system('cls')
    selection = input('(1) FBCAD or (2) HCAD > ')
    go_to(selection)


def go_to(selection):
    """
    Processes the User selection to route the script
    Enables functionality to go back to start_program()
    """

    if selection == '1':
        # Ask the user for the address to search
        print('\nFort Bend County selected. Enter (x) to go back.\n')
        query = input("Enter Property Address > ")

        # If user inputs x, restart the program
        if query.lower() == 'x':
            start_program()

        else:
            # Running a search on the address
            print("\nSearching...")
            result = fbcad.get_property_id(query.strip())

            # Checking if the property was found
            if result:
                pyperclip.copy(format_result(result))

            else:
                print(f'\nNo Results for: {query.strip()}')
                os.system('pause')
                start_program()

    elif selection == '2':
        # Ask the user for the address to search
        print('\nHarris County selected. Enter (x) to go back.\n')
        query = input("Enter Property Address > ")

        # If user inputs x, restart the program
        if query.lower() == 'x':
            start_program()

        else:
            # Split the inputted address into street number and street name using regex
            # Find all the numbers at the start of the address
            street_number = re.findall(r'^[0-9]*', query)[0]
            # Find all the characters in the address that are not numbers
            street_name = re.findall(r'[^0-9]+', query)[0].strip()

            # Running a search on the address
            print("\nSearching...")

            try:
                result = hcad.get_data(stnum=street_number, stname=street_name)

            except AttributeError:
                result = None

            # Checking if the property was found
            if result:
                pyperclip.copy(format_result(result))

            else:
                print(f'\nNo Results for: {query.strip()}')
                os.system('pause')
                start_program()

    else:
        start_program()


start_program()
