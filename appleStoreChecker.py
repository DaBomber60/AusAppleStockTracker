import pandas as pd
import flat_table as ft
from twilio.rest import Client
from datetime import datetime
import sys
import time

model = input('Input model of iPhone to check for: [MQ9X3ZP/A] ') or 'MQ9X3ZP/A'
postcode = input('Enter your Australian postcode: [2000] ') or '2000'
region = ''

storeStock = {}

if len(postcode) == 4:
    region = 'AU'
else:
    print('Invalid postcode input')

#SIGN UP FOR A FREE TWILIO ACCOUNT HERE: https://www.twilio.com/try-twilio

account_sid = 'TWILIO_ACCOUNT' #ENTER YOUR TWILIO ACCOUNT SECRET ID HERE
auth_token = 'TWILIO_TOKEN' #ENTER YOUR TWILIO AUTH TOKEN HERE
client = Client(account_sid, auth_token)

if region == 'AU':
    apiStart = 'https://www.apple.com/au/shop/fulfillment-messages?pl=true&mts.0=regular&parts.0='
    apiMid = '&location='

apiBuilt = apiStart+model+apiMid+postcode

while(True):
    data = pd.read_json(apiBuilt)
    df = pd.DataFrame.from_records(data)
    dfFlat = ft.normalize(df)
    dfResult = dfFlat.filter(items=['body.pickupMessage.stores.retailStore.address.companyName','body.pickupMessage.stores.partsAvailability.'+model+'.pickupSearchQuote'])
    dfResult.drop_duplicates(inplace=True)
    dfResult.dropna(inplace=True)
    dfResult.reset_index(drop=True,inplace=True)
    dfResult.rename(columns={
        'body.pickupMessage.stores.retailStore.address.companyName': 'Store Name',
        'body.pickupMessage.stores.partsAvailability.'+model+'.pickupSearchQuote': 'Availablity'
    },inplace=True)

    for i in range(len(dfResult)):
        storeStock.update({(dfResult.at[int(i),'Store Name']): (dfResult.at[int(i),'Availablity'])})

    for i in storeStock:
        if storeStock[i] != 'Currently unavailable':
            print('{i} has stock!')
            message = client.messages .create(
                body =  i+' has stock!',
                from_ = '+1##########', #ENTER YOUR TWILIO VIRTUAL NUMBER HERE
                to = '+61400000000') #ENTER YOUR TWILIO VERIFIED TARGET NUMBER HERE
            message.sid
            sys.exit()
    time.sleep(60)