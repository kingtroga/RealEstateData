# Import the Libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup


# The task functions
def getCorrectPinFormat(pin):
    """
    INPUT: 124013000010000 : int
    OUTPUT: '01-24-01-300-001-0000' : str
    """
    pin = str(pin)
    if len(pin) == 15:
        returnString = (
            '0' + pin[0] + '-'+
            pin[1] + pin[2] + '-' +
            pin[3] + pin[4] + '-' +
            pin[5] + pin[6] + pin[7] + '-' +
            pin[8] + pin[9] + pin[10] + '-' +
            pin[11] + pin[12] + pin[13] + pin[14]
             )
        return returnString
    else:
        raise Exception("The PIN String is invaild")

def getPageContent(pin):
    session = requests.Session()
    headers = {
    'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cookie': 'mp_52e5e0805583e8a410f1ed50d8e0c049_mixpanel=%7B%22distinct_id%22%3A%20%22182a72924525c4-0d5f11dbe584a-26021d51-100200-182a7292453226%22%2C%22%24device_id%22%3A%20%22182a72924525c4-0d5f11dbe584a-26021d51-100200-182a7292453226%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%7D'
    }
    #print("PIN: ", pin)
    url = (
    'https://willcountysoa.com/propertysearch/detail.aspx?Mpin=' 
    + pin)
    #print("URL: ", url)

    response = session.get(url, headers=headers)
    return response.text

def isPageActive(pageContent):
    return True

def getPageTable(pageContent):
    table = pageContent.find('table', {'id':'FormView1_GridView2'})
    #print(table.get_text())
    return table
    
def checkTableHeaders(table):
    try:
        tableRows = table.find_all('tr')
        tableHeaders = tableRows[0].find_all('th')
    except AttributeError as e:
        return ("ERROR", e)
    
    flag1 = tableHeaders[7].text.strip()
    flag2 = tableHeaders[0].text.strip()
    flag3 = tableHeaders[1].text.strip().replace(" ", '')

    condition1 = (flag1 == 'MarketValue')
    condition2 = (flag2 == 'Year')
    condition3 = (flag3 == 'AssessLevel')

    if condition1 and condition2 and condition3:
        return True
    else:
        return ("Error", False)

def getValues(table):
    try:
        tableRows = table.find_all('tr')
        secondRow = tableRows[1].find_all('td')
    except AttributeError as e:
        return False

    marketValue = secondRow[7].text
    year = secondRow[0].text
    assessLevel = secondRow[1].text

    return (marketValue, year, assessLevel)

# The task at hand
df = pd.read_csv('all_will_country_pins.csv')

pins = []
marketValues = []
years = []
accessValues = []
isActive = []
errors = []


for pin in df['PIN'][:50]:
    pin = getCorrectPinFormat(pin)
    pins.append(pin)

    pageContent = getPageContent(pin)


    if type(pageContent) is tuple:

        # There was an error in handling this particular pin
        
        errors.append(pageContent)
        marketValues.append(None)
        years.append(None)
        accessValues.append(None)
        isActive.append(None)
        

    pageContent = BeautifulSoup(pageContent, 'html.parser')

    if isPageActive(pageContent):
        table = getPageTable(pageContent)
        
        if table is not None:
            
            if checkTableHeaders(table):
                
                marketValue, year, accessValue = getValues(table)
                errors.append(None)
                marketValues.append(marketValue)
                years.append(year)
                accessValues.append(accessValue)
                isActive.append(True)


            else:
                errors.append("The headers doesn't match our logic")
                marketValues.append(None)
                years.append(None)
                accessValues.append(None)
                isActive.append(None)


        else:
            errors.append("Table doesn't exist")
            marketValues.append(None)
            years.append(None)
            accessValues.append(None)
            isActive.append(None)
            

            
    else:
        errors.append("This Parcel is no longer active")
        marketValues.append(None)
        years.append(None)
        accessValues.append(None)
        isActive.append(False)

data = {
    'Pins': pins,
    'Market Value': marketValues,
    'Year': years,
    'Access Value': accessValues,
    'IsActive': isActive,
    'Error': errors
}   


df2 = pd.DataFrame(data)
df2.to_csv("realEstateDataResult.csv", index=False) # an a clause that chatchs opened i.e when file is open
