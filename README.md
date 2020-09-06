# Python-Web-Crawler
 
This is the code for crawling any website of your choice, in this case flinkhub.com. 
The root url will have to be entered manually in the MongoDB database, in the form
of a json object with the relevant fields.


Example:- (change "Link" according to your choice)


{
    "Link" : "https://flinkhub.com",
    "Source Link" : "",
    "Is Crawled" : false,
    "Last Crawled Dt" : null,
    "Response Status" : 0,
    "Content type" : "",
    "Content length" : 0,
    "File path" : "",
    "Created at" : ISODate("2020-08-29T12:46:00.000Z")
}


### Run locally from command line


- Install virtual environment first


pip install virtualenv


- Set up virtual environment


virtualenv myproject


- Activate virtual environment


(Linux) $ source myproject/bin/activate

(Windows) > myproject\Scripts\activate


-Install dependencies


pip install -r requirements.txt



- To start crawling process


python3 crawler.py
