# Dotproperty Scraper

Python script to scrape https://www.dotproperty.co.th/en

## Prerequisites:
- Python 3.7
- MySQL Server
- ChromeDriver -> Same version of your Google Chrome.
- Python libraries ->os, glob, urllib, requests, BeautifulSoup, selenium, mysql and getpasss.

## Installing
- Use pip to install the libraries. Example: pip install urllib
- ChromeDriver has to be in the same directory of the program.

## Running
To run the program you just need to enter the url, database user and password 
(hidden). 
The program will be inserting the information in the tables of the database. 
The images will be storaged at galleries/asset_code folder.

## Usage steps

1.  Run dotproperty_scraper.py: python dotproperty_scraper.py

2. Enter url, database user and password

![alt text](https://github.com/vjmoreno/dotproperty_scraper/blob/master/readme_images/1.png)

3. The program will automatically start collecting the data from the properties and saving it in the database.  The database is automatically created, you just need your username and password to connect. The data is in the tables: myproperty.dotproperty and myproperty.dotproperty_image  
The images will be stored at ‘galleries’ folder. The images coming from the same property will be stored in the same folder (folder’s name =  asset code).

![alt text](https://github.com/vjmoreno/dotproperty_scraper/blob/master/readme_images/2.png)

![alt text](https://github.com/vjmoreno/dotproperty_scraper/blob/master/readme_images/3.png)

![alt text](https://github.com/vjmoreno/dotproperty_scraper/blob/master/readme_images/4.png)

![alt text](https://github.com/vjmoreno/dotproperty_scraper/blob/master/readme_images/5.png)
