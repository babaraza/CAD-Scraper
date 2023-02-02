# Creating a House object to organize the results for easier access
class House:
    def __init__(self, address, sqft, value, year_built, porch, patio, deck, garage, purchase_date, buyer, bedrooms,
                 baths, half_baths, fireplace, stories, elements):
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
        self.half_baths = half_baths
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

    if not house.half_baths or house.half_baths == 0:
        bathroom_template = house.baths
    else:
        bathroom_template = f'{house.baths} full {house.half_baths} half'

    template = f"""
{house.address}

STORY      : {house.stories}
YEAR BUILT : {house.year_built}
SQ FOOT    : {house.sqft}
BATHROOMS  : {bathroom_template}
FIREPLACE  : {house.fireplace}
ROOF REPL  :
EXTERIOR   : 
GARAGE     : {house.garage}
OPEN PORCH : {house.porch}
PATIO      : {house.patio}
WINDOW     : 
PAY        : 
BOUGHT     : {house.purchase_date}
MARKET VAL : {house.value}
FLOOD QUOTE:

Raw Data:
Owner: {house.buyer}
{raw_data}
"""

    old_template = f"""
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
WINDOW     : 
DOGS       : 
PAY        : 
EXTERIOR   : 
BOUGHT     : {house.purchase_date}
MARKET VAL : {house.value}
FLOOD QUOTE: 

Raw Data:
Owner: {house.buyer}
{raw_data}
"""
    return template
