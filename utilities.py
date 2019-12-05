# Creating a House object to organize the results for easier access
class House:
    def __init__(self, address, sqft, value, year_built, porch, patio, deck, garage, purchase_date, buyer, bedrooms,
                 baths, fireplace, stories, elements):
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
        self.stories = stories
        self.elements = elements


def format_result(house):
    """
    Formats the result from the house object into the template

    :param house: An instance of the House object
    :return: A string containing the formatted template with data
    """

    # Getting the raw data i.e. elements retrieved from the CAD website
    # this is to double check the decks, porch, patio etc
    raw_data = ""
    for k, v in house.elements:
        raw_data += f'{k}: {v}\n'

    template = f"""
{house.address}

STORY      : {house.stories}
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

Raw Data:
{raw_data}
"""
    return template
