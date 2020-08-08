# fragrantica_scraper

Python script to scrape https://www.fragrantica.com/

## Prerequisites:
- Python 3.7
- ChromeDriver -> Same version of your Google Chrome.
- Python libraries ->os, csv, requests, urllib and selenium

## Installing
- Use pip to install the libraries. Example: pip install urllib
- ChromeDriver has to be in the same directory of the program.

## Usage steps
1. Go to https://www.fragrantica.com/search/ and enter your search parameters, like the brand or gender.
2. Copy the url.
3. Run dotproperty_scraper.py and paste the url. Example of url: https://www.fragrantica.com/search/?dizajner=Alkemia%20Perfumes&spol=female
The max number of perfumes that the program can get from each search is 1000.
4. The program will start downloading the information. The pictures will be stored at ./gallery/brand_name. 
The csv file generated is fragrantica.csv.
All the content is accumulative, so if you want to get just the perfumes of the next search, delete the files before running the program.
