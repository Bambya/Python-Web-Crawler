# Python-Web-Crawler
 
This is the code for crawling any website of your choice, in this case flinkhub.com. 
The root url will have to be entered manually in the MongoDB database, in the form
of a json object with the relevant fields.


Example:- (change "Link" according to your choice)


{
    "Link" : "https://letterboxd.com",
    "Source_Link" : "",
    "Is_Crawled" : false,
    "Last_Crawled_Dt" : null,
    "Response_Status" : 0,
    "Content_Type" : "",
    "Content_Length" : 0,
    "File_Path" : "",
    "Created_At" : ISODate("2020-08-29T12:46:00.000Z")
}


### Run locally from command line


- First download and install MongoDB and a GUI tool of your choice (Robo 3T is a good option)



- Install virtual environment first


   pip install virtualenv


- Set up virtual environment with name myproject


   virtualenv myproject


- Activate virtual environment


   (Linux) $ source myproject/bin/activate


   (Windows) > myproject\Scripts\activate


- Install dependencies


   pip install -r requirements.txt



- To start crawling process


    python3 crawler.py
