# Author: Giulio Savian
# Function: web_scraper()

#IMPORT LIBRARIES
from selenium import webdriver
from bs4 import BeautifulSoup
from threading import Timer
import sched
import requests
from queue import Queue
from statistics import mean
import pandas as pd
#from skimage import io

#INPUT
# @Link : vinted, subito, ...
# @Search: what I want to search
#OUTPUT
# @Products, prices, categories, images, links

def web_scraper(Search):
    
    global products, prices, categories, images, links, product_data

    products    = []    #List to store name of the product
    prices      = []    #List to store price of the product
    categories  = []    #List to store rating of the product
    images     = []    #List of Immages
    links       = []    #List of Links
    product_data = [] #Is a list containing lists [products,prices]

    #select the web browser
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")

    #Will navigate to a page given by the URL forget
    baselink = 'https://www.vinted.it/catalog?search_text='
    filters = '&order=newest_first'
    driver.get(baselink + Search + filters)
    
    #get source code 
    content = driver.page_source
    
    soup = BeautifulSoup(content,features="html.parser")
    soup.prettify()
    #scraping the page
    for page in soup.findAll('div', attrs={"data-testid" : "grid-item"}):

        #scraping the boxes
        for box in page.findAll('div', attrs={"class" : "new-item-box__container"}):


            #scraping the name the prize and the link for on a single box
            advertisement = []

            #CATEGORY
            tmp = box.find('div', attrs={'new-item-box__description'})
            category = tmp.find('h4', attrs={'web_ui__Text__text web_ui__Text__caption web_ui__Text__left'})
            #print(tmp.text)
            #print(category.text)
            categories.append(category.text)
            advertisement.append(category.text)
            #print(category.text)
            #print("OK category")

            #PRICE
            price = box.find('div', attrs={'title-content'})
            price_raw = price.text
            price_clean = price_raw.replace('\xa0', '')
            prices.append(price_clean)
            advertisement.append(price_clean)
            #print("OK price")

            #LINK
            tmp = box.find('div', attrs={'class' : 'u-position-relative u-min-height-none u-flex-auto'})
            #print(tmp)
            link = tmp.find('a')
            #print(link)
            links.append(link.get('href'))
            advertisement.append(link.get('href'))
            #SUBCATEGORY

            #IMMAGE and PRODUCT
            tmp = box.find('div', attrs={'web_ui__Image__image web_ui__Image__cover web_ui__Image__portrait web_ui__Image__scaled web_ui__Image__ratio'})
            image_link  = tmp.find('img')
            products.append(image_link.get('alt'))
            #image = io.imread(image_link.get('src'))
            #images.append(image)
            #print(image.get('alt'))
            #print(image.get('src'))
            #advertisement.append(image_link.get('alt'))
            #advertisement.append(image) #Wrong
            #product_data.append(advertisement) # contanins all the data grupped 



    #Reduce lenth
    products = products[0:5]
    prices = prices[0:5]
    categories = categories[0:5]
    links = links[0:5]
    images = images[0:5]

    for i in range(len(products)):
        p = products[i]
        pr = prices[i]
        product_data.append([p,pr,links[i]])

    #print(prices)
    #print(categories)
    #print(links)
    #print(images)
    #print(product_data)

    return products, prices, categories, links, images, product_data


def isnew(new_products, old_products):
    potential_products = []
    #print(products_data)
    #print("old product:")
    #print(old_products)
    for product in new_products:
        if product[0] not in old_products.queue:            
            potential_products.append(product)
            old_products.put(product)
    return potential_products

def scrape_prices_ebay(product_list):
    prices = {}
    for product_data in product_list :
        product = product_data[0]
        price = []
        #print(f"The product under analysis is: {product}")
        # format the search query
        search_query = product.replace(' ', '+')
        # send a request to eBay's search page
        response = requests.get(f'https://www.ebay.com/sch/i.html?_nkw={search_query}&LH_Complete=1&LH_Sold=1')
        soup = BeautifulSoup(response.content, 'html.parser')
        soup.prettify()
        # extract the first result from the search results 
        First = True
        #try:
        num = 0
        for result in soup.findAll('span', attrs={'class': 's-item__price'}):

            #print(f'Scraped string,{result}')
            if First == True:
                #print('First discrarded')
                First = False
                continue
            else:
                if "to" in result.text:
                    #print('Contains (to)')
                    continue
                else:
                    str = result.text
                    num = str.replace("$", "")
                    num = num.replace("€", "")
                    num = float(num.replace(",", ""))
                    num_round = round(num,2)
                    price.append(num_round)
                    #print(f'Single price,{price}')

        if len(price)>0:
            average_price = mean(price)
            max = average_price*10
            min = average_price/10

        for i in price:
            if i > max or i< min:
                price.remove(i)

        if len(price)>0:
            average_price = mean(price)


        #print(f'Average price,{average_price}')
        prices[product] = average_price
        
    print(f'Number of potential products:{len(product_list)}')
        #except:
        #    print(f'Error scrape_prices_ebay,{str}')
        #    prices[product] = 'Not found'
            
    return prices

def compare_prices(marketprices,potential_products):
    m_prices = list(marketprices.values())
    good_indeces = []
    bad_indeces = []
    count = 0

    for m_price in m_prices:
        product = potential_products[count]
        price = product[1]
        #print(price)
        tmp = price.replace("$", "")
        tmp = tmp.replace("€", "")
        tmp = float(tmp.replace(",", "."))

        if tmp < m_price * 0.5:
            good_indeces.append(count)
        else:
            bad_indeces.append(count)
        
        print(f'Vinted price: {tmp}')
        print(f'Ebay price: {m_price}')
        
        count +=1

    #Repo
    print(f'N. good product: {len(good_indeces)}')
    print(f'good indeces: {good_indeces}')
    print(f'good indeces: {bad_indeces}')
    
    return good_indeces, bad_indeces


def algorithm():

    #Call scrape function
    web_scraper(mex)
    print('Web_scraper function OK')

    #Check new products
    potential_products = isnew(product_data, old_products_fifo)
    #print(f"New products inserted:{potential_products}")
    print('Is_new function OK')

    #scrape the new products prizes on the web
    marketprices = scrape_prices_ebay(potential_products)
    print(f"Market price calculated:{marketprices}")
    print('scrape_prices_ebay function OK')
    
    #compare product price
    good_indeces, bad_indeces = compare_prices(marketprices,potential_products)
    print('compare_prices function OK')
    
    #generate advertisement for good indeces
    m_prices = list(marketprices.values())

    good_products = []
    for i in good_indeces:
        #print(f"Value:{potential_products[i][1]}")
        #print(f"Market price:{m_prices[i]}")
        good_product = potential_products[i]
        price = round(float(m_prices[i]), 2)
        print(price)
        good_product.append(str(price)+'€')
        good_products.append(good_product)

    print('algorithm OK')
    return good_products
    

def init(Message):
    #INIT GLOBAL VAR
    global old_products_fifo
    global products, prices, categories, images, links, product_data
    global mex
    #INIT 
    mex = Message
    web_scraper(Message)
    old_products_fifo = Queue(1000)
    print('Initializzation completed!')

def main(Message, Run):
    #global gRun
    #gRun = Run
    #while gRun:
    good_products = algorithm()
    print(good_products)
    return good_products

def scraper_reset():
    old_products_fifo = None
    products = None
    prices =  None
    categories = None
    images = None
    links = None
    product_data = None