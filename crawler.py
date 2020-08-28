import requests
import pymongo
import re
import string
import random
import os.path
import traceback
from datetime import datetime as dt
from datetime import timedelta as td
from bs4 import BeautifulSoup as bsoup
from config import config
from logger import logger
from time import sleep
from functions import convert_to_ist, save_file, save_html_file, get_file_name

month_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


#main crawling function
def crawl():

    #initialize cycle
    cycle = 1

    while True:

        time_before_24hrs = dt.now() - td(days=config["link_refresh_time"])             #This was the time 24 hours before this current time

        #Check collection for links that were either never crawled or were crawled more than 24 hours ago
        crawlable_documents = mycol.find( {'$or': [ {"Is Crawled": False  }, {"Last Crawled Dt": {'$lt': time_before_24hrs} } ] } )
        print("Size of all docs = ", mycol.count_documents({}))
        print("Size of crawlable docs = ", mycol.count_documents({'$or': [ {"Is Crawled": False }, {"Last Crawled Dt": {'$lt': time_before_24hrs} } ]}))

        for document in crawlable_documents:

            response_status = requests.head(document["Link"], allow_redirects=True).status_code
            content_type = requests.head(document["Link"], allow_redirects=True).headers['content-type']
            print(response_status, content_type)

            if response_status != 200:

                mycol.update_one({'_id': document['_id']}, {'$set': {"Is Crawled": True, "Last Crawled Dt": dt.now() } } )
                continue

            if 'text/html' not in content_type:

                #give appropriate name and save file
                r = requests.get(document['Link'])
                file_name = get_file_name(content_type)
                save_file(file_name, r)

                mycol.update_one({ '_id' : document['_id']}, {'$set': {"Is Crawled": True, "Last Crawled Dt": dt.now() } } )
                continue

            try:
                logger.debug("Making HTTP GET request: " + document['Link'])
                r = requests.get(document['Link'])
                res = r.text
                logger.debug("Got HTML source, content length = " + str(len(res)))
            except:
                logger.exception("Failed to get HTML source from " + document['Link'])
                continue

            mycol.update_one({ '_id' : document['_id']}, {'$set': {"Is Crawled": True, "Last Crawled Dt": dt.now() } } )

            #Generate string of random characters
            file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))

            #Save html file to disc in a folder named HTML files
            save_html_file(file_name, r)

            logger.debug("Extracting links from the HTML")

            soup = bsoup(res, 'html.parser')

            tags = soup('a')

            if len(tags) == 0:
                continue

            for tag in tags:

                get_link(tag, mycol, document)



            print("Number of links crawled = ", mycol.count_documents({}))

        '''end of cycle, sleep for 5 seconds'''
        print("Number of links crawled = ", mycol.count_documents({}))
        print("End of Cycle " + str(cycle) + ", sleeping for " + str(config["sleep_time"]) + " secs")
        sleep(config["sleep_time"])

        if mycol.count_documents({}) >= config["max_links"]:
            print('Maximum limit of links reached')
            break

        cycle += 1                                                   #Increment cycle
        print("Start of cycle " + str(cycle))


def get_link(tag, mycol, document):
    url = tag.get('href')

                if(url):
                    valid_link = re.findall('^http.*|^/.*', url)               # link is valid if it starts from 'http' or starts with '/' (relative link)

                #get link parameters/table columns
                if valid_link:

                    link = valid_link.pop(0)

                    if not link.startswith('http'):                                 # if link is not absolute add root url to it

                        if document["Link"][-1] == '/':
                            link = link[1:]                                             # to avoid 2 / signs

                        link = document["Link"] + link

                    if mycol.count_documents({'Link': link}, limit=1) != 0:
                        continue

                    '''get date parameters - year, month, day, hour, min and seconds using
                    response headers and the regex library'''
                    datetime = requests.head(link, allow_redirects=True).headers['date']

                    datetime = datetime.split()                                     #Before splitting, date is in this format:- Mon, 24 Aug 2020 14:18:38 GMT

                    time = re.findall('[0-9]+', datetime[4])                        #datetime[4] contains time in the format hour:minutes:seconds

                    time_params = {"year": int(datetime[3]),
                                    "month": int(month_dict[datetime[2]]),          #month_dict helps us to convert name of month from three letter strings to month number
                                    "day": int(datetime[1]),
                                    "hour": int(time[0]),
                                    "mins": int(time[1]),
                                    "sec": int(time[2])}

                    utc_time = dt(time_params['year'], time_params['month'], time_params['day'], time_params['hour'], time_params['mins'], time_params['sec'])

                    source_link = document['Link']

                    is_crawled = False                                                      #initially link won't be crawled

                    last_crawled_date = 0

                    response_status = requests.head(link, allow_redirects=True).status_code

                    try:
                        content_type = requests.head(link, allow_redirects=True).headers['content-type']
                    except:
                        continue

                    content_length = len(requests.get(link, allow_redirects=True).content)

                    file_path = './HTML Files'

                    created_at = convert_to_ist(utc_time)

                    link_params = {"Link": link, "Source Link": source_link, "Is Crawled": is_crawled, "Last Crawled Dt": last_crawled_date, "Response Status": response_status,
                                    "Content type": content_type, "Content length": content_length, "File path": file_path, "Created at": created_at}

                    #insert document in collection
                    x = mycol.insert_one(link_params)
                    print(link_params["Link"])


if __name__ == "__main__":

    #Create mongodb database and collection(table)
    myclient = pymongo.MongoClient(config['local_host'])
    mydb = myclient["mydatabase"]
    mycol = mydb["crawler_links"]

    logger.debug('Starting process')

    logger.debug('Getting links in database')

    while True:
        main_task()

    '''crawl()

    logger.debug('Process complete')'''



