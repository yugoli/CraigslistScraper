import gmail
import time
import email
import string
import requests
from bs4 import BeautifulSoup as bs4
import numpy as np
from time import sleep

def find_price(results):
    price = 0
    price = results.find('span', {'class': 'price'})
    '''if price is not None:
        price = float(price.text.strip('$'))
    else:
        price = np.nan'''

    return price.text


#fill in info login below & must change your gmail account settings to allow less secure apps
gm = gmail.GMail('my_username', 'my_password')
gm.connect()

base_url = 'http://sfbay.craigslist.org'
url = base_url + '/search/sfc/apa?search_distance=1&postal=94103&min_price=2500&max_price=3000&bedrooms=1&bathrooms=1'

# This will remove weird characters that people put in titles like ****!***!!!
use_chars = string.ascii_letters + ''.join([str(i) for i in range(10)]) + ' '

link_list = []  # We'll store the data here
link_list_send = []  # This is a list of links to be sent
send_list = []  # This is what will actually be sent in the email

# Careful with this...too many queries == your IP gets banned temporarily
while True:
    resp = requests.get(url)
    txt = bs4(resp.text, 'html.parser')
    apts = txt.findAll(attrs={'class': "row"})
    
    # We're just going to pull the title and link
    for apt in apts:
        title = apt.find_all('a', attrs={'class': 'hdrlnk'})[0]
        name = ''.join([i for i in title.text if i in use_chars])
        price = find_price(apt)
        link = title.attrs['href']
        if link not in link_list and link not in link_list_send:
            print('Found new listing')
            link_list_send.append(link)
            #formatted_link = '<a href="{0}">link</a>'.format(base_url+link)
            send_list.append(price + ' ' + name + '  -  ' + base_url+link)
            
    # Flush the cache if we've found new entries
    if len(link_list_send) > 0:
        print('Sending mail!')
        msg = '\n'.join(send_list)
        m = email.message.Message()
        m.set_payload(msg)
        gm.send(m, ['li.liang1@gmail.com'])
        link_list += link_list_send
        link_list_send = []
        send_list = []
    
    # Sleep a bit so CL doesn't ban us
    sleep_amt = np.random.randint(60, 120)
    time.sleep(sleep_amt)