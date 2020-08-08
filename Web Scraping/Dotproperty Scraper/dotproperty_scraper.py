
import os
import glob
import requests
import mysql.connector
from getpass import getpass
from bs4 import BeautifulSoup 
from selenium import webdriver
from urllib.request import Request, urlopen
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class DotProperty_scraper:

	def __init__(self, url, user, password):
		#database user
		self.user = user
		#database password
		self.password = password
		#chromedriver path
		self.path = './chromedriver.exe'
		#hide Chrome browser
		self.chrome_options = Options()
		self.chrome_options.add_argument("--headless")
		#main url
		self.url = url
		#list for urls of the properties
		self.url_list = []
		#list of properties
		self.properties_list = []

	def run(self):
		self.create_database()
		self.get_urls()
		self.get_data()

	def get_urls(self):
		#get html of the first page
		source = requests.get(self.url, headers={"User-Agent":"Mozilla/5.0"}).text
		soup = BeautifulSoup(source, 'lxml')
		#find all the urls of the properties listed on the first page
		match = soup.find_all(title='Details')
		match = [link['href'] for link in match]
		#add the urls to the list
		self.url_list.extend(match)
		#number of properties found
		results_found = int(soup.find(id='properties_total').text)
		#number of pages to scrape, which can be maximum 40 (restricted by the webpage)
		n_pages = max(results_found/25, 40)
		#repeat the process for every page
		for page in range(2, 3):
		#for page in range(2, n_pages + 1):
			source = requests.get(self.url + '&page={}'.format(page), headers={"User-Agent":"Mozilla/5.0"}).text
			soup = BeautifulSoup(source, 'lxml')
			match = soup.find_all(title='Details')
			match = [link['href'] for link in match]
			self.url_list.extend(match)

	def get_data(self):
		for url in self.url_list:
			try:
				property_dict = {}
				driver = webdriver.Chrome(self.path, options=self.chrome_options)
				driver.get(url)
				#image
				gallery = driver.find_element_by_id('hiddenGallery')
				gallery_links_list = [li.get_attribute('data-src') for li in gallery.find_elements_by_tag_name("li")]
				property_dict['gallery_links'] = gallery_links_list
				#sale and rent price
				price = driver.find_element_by_class_name('price-title').text.split('\n')
				property_dict['price'] = price
				#bedrooms, bathrooms and space
				key_features_list = driver.find_element_by_class_name('key-featured').text.split('\n')
				property_dict['key_features_list'] = key_features_list
				#location
				location = driver.find_element_by_class_name('location').text
				property_dict['location'] = location
				#description - title
				description_title = driver.find_element_by_class_name('custom-title').text
				property_dict['description_title'] = description_title
				#description - text
				description_text = driver.find_element_by_class_name('text-description').text
				property_dict['description_text'] = description_text
				#facility - amenity
				facilities = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/div/div/div[8]/ul')
				facilities_list = [li.text for li in facilities.find_elements_by_tag_name("li")]
				property_dict['facilities_list'] = facilities_list
				#project info
				project_info = driver.find_element_by_class_name('user-company-detail').find_element_by_tag_name('p').text
				property_dict['project_info'] = project_info
				#map
				latitude = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/div/div/div[5]/meta[1]').get_attribute("content")
				longitude = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/div/div/div[5]/meta[2]').get_attribute("content")
				property_dict['latitude'] = latitude
				property_dict['longitude'] = longitude
				#contact info
				description = driver.find_element_by_class_name('text-description')
				contact_info = ''
				for form in description.find_elements_by_tag_name('form'):
					data_mode = form.find_element_by_tag_name('span').get_attribute('data-mode')[5:].replace('-', ' ')
					data_detail = form.find_element_by_tag_name('span').get_attribute('data-detail')
					contact_info += '{}: {}\n'.format(data_mode, data_detail)
				property_dict['contact_info'] = contact_info
				#page title
				page_title_element = driver.find_element_by_class_name('page-title')
				page_title = page_title_element.find_element_by_tag_name('a').text
				property_dict['page_title'] = page_title
				#asset code
				asset_code = driver.find_element_by_class_name('internal-ref').text[12:]
				property_dict['asset_code'] = asset_code
				#url
				property_dict['url'] = url 
				#create new property and add it to the database
				p = Property(property_dict)
				conection = mysql.connector.connect(host="localhost",
										user= self.user,
										password= self.password,
										database = 'myproperty',
										auth_plugin='mysql_native_password')
				cursor = conection.cursor()
				mySql_insert_query = """INSERT INTO myproperty.dotproperty 
													(ASSET_CODE, PAGE_TITLE, 
													PRICE, BED_AMOUNT, BATH_AMOUNT, 
													SPACE, LOCATION, DESCRIPTION, 
													FACILITIES, PROJECT_INFO, LATITUDE, 
													LONGITUDE, CONTACT) 
													VALUES 
													(%s, %s, %s, %s, %s, %s, %s, %s, 
													%s, %s, %s, %s, %s)"""
				cursor.execute(mySql_insert_query, (p.asset_code, p.page_title, p.price, 
								p.bed, p.bath, p.space, p.location, p.description, 
								p.facilities, p.project_info, p.latitude, p.longitude, 
								p.contact_info))
				mySql_insert_query = """INSERT INTO myproperty.dotproperty_image 
													(ASSEST_CODE, PATH_, IMAGE_URL) 
													VALUES (%s, %s, %s)"""
				cursor.execute(mySql_insert_query, ( p.asset_code, p.gallery.path, '\n'.join(p.gallery.gallery_links)))
				conection.commit()
				cursor.close()
				conection.close()
				#close browser
				driver.quit()
				
			except:
				pass

	def create_database(self):
		conection = mysql.connector.connect(host="localhost",
									user= self.user,
									password=self.password,
									auth_plugin='mysql_native_password',)
		cursor = conection.cursor()
		#cursor.execute('''DROP DATABASE IF EXISTS `myproperty`;''')
		cursor.execute("""CREATE SCHEMA IF NOT EXISTS `myproperty` 
						DEFAULT CHARACTER 
						SET utf8 COLLATE utf8_unicode_ci ;""")
		conection.commit()
		cursor.close()
		conection.close()
		conection = mysql.connector.connect(host="localhost",
									user=self.user,
									password=self.password,
									auth_plugin='mysql_native_password',
									database='myproperty')
		cursor = conection.cursor()
		cursor.execute("""CREATE TABLE IF NOT EXISTS `dotproperty` (
		`ASSET_ID` int(11) NOT NULL AUTO_INCREMENT,
		`ASSET_CODE` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
		`PAGE_TITLE` varchar(3000) COLLATE utf8_unicode_ci NOT NULL,
		`PRICE` decimal(13,2) DEFAULT NULL,
		`BED_AMOUNT` int(11) DEFAULT NULL,
		`BATH_AMOUNT` int(11) DEFAULT NULL,
		`SPACE` decimal(10,4) DEFAULT NULL,
		`LOCATION` varchar(3000) COLLATE utf8_unicode_ci DEFAULT NULL,
		`DESCRIPTION` longtext COLLATE utf8_unicode_ci,
		`FACILITIES` longtext COLLATE utf8_unicode_ci,
		`PROJECT_INFO` longtext COLLATE utf8_unicode_ci,
		`LATITUDE` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
		`LONGITUDE` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,   
		`CONTACT` varchar(3000) COLLATE utf8_unicode_ci DEFAULT NULL,
		`CREATED_DATE` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
		`UPDATE_DATE` datetime DEFAULT NULL,
		PRIMARY KEY (`ASSET_ID`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;""")
		cursor.execute("""CREATE TABLE IF NOT EXISTS `dotproperty_image` (
		`IMAGE_ID` int(11) NOT NULL AUTO_INCREMENT,
		`ASSEST_CODE` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
		`PATH_` varchar(1000) COLLATE utf8_unicode_ci DEFAULT NULL,
		`IMAGE_URL` longtext COLLATE utf8_unicode_ci,
		`CREATED_DATE` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
		`UPDATED_DATE` datetime DEFAULT NULL,
		PRIMARY KEY (`IMAGE_ID`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;""")
		conection.commit()
		cursor.close()
		conection.close()
		conection = mysql.connector.connect(host="localhost",
									user=self.user,
									password=self.password,
									auth_plugin='mysql_native_password',
									database='myproperty')
		cursor = conection.cursor()
		conection.commit()
		cursor.close()
		conection.close()


			

class Property:

	def __init__(self, property_dict):
		self.property_dict = property_dict
		self.prepare_attr()
		


	def prepare_attr(self):
		self.asset_code = self.property_dict['asset_code']
		self.gallery = Gallery(self.property_dict['gallery_links'], self.asset_code)
		self.page_title = self.property_dict['page_title']
		self.price = float(int(self.property_dict['price'][0].split(' ')[2].replace(',', '')))
		self.bath = 0
		self.bed = 0
		self.space = 0.0
		for x in range(len(self.property_dict['key_features_list'])):
			if self.property_dict['key_features_list'][x] in ['Bath', 'Baths']:
				self.bath = int(self.property_dict['key_features_list'][x - 1])
			elif self.property_dict['key_features_list'][x] in ['Bed', 'Beds']:
				self.bed = int(self.property_dict['key_features_list'][x - 1])
			elif self.property_dict['key_features_list'][x] == 'Usable area':
				self.space = float(self.property_dict['key_features_list'][x - 1][:-3].replace(',',''))
		self.location = self.property_dict['location']
		self.description = self.property_dict['description_title']+ '\n' +self.property_dict['description_text']
		self.facilities = '\n'.join(self.property_dict['facilities_list'])
		self.project_info = self.property_dict['project_info']
		self.latitude = self.property_dict['latitude']
		self.longitude = self.property_dict['longitude']
		self.contact_info = self.property_dict['contact_info']
		self.page_title = self.property_dict['page_title']
		self.asset_code = self.property_dict['asset_code']
		self.url = self.property_dict['url']
		print('New property downloaded: {}'.format(self.url))
		print('1.-', self.gallery)
		print('2.-', self.price)
		print('3.-', self.bath, self.bed)
		print('4.-', self.space)
		print('5.-', self.location)
		print('6.-', self.description)
		print('7.-', self.facilities)
		print('8.-', self.project_info)
		print('9.-', self.latitude, self.longitude)
		print('10.-', self.contact_info)
		print('11.-', self.page_title)
		print('12.-', self.asset_code)



class Gallery:

	def __init__(self, gallery_links, asset_code):
		self.gallery_links = gallery_links
		self.asset_code = asset_code
		self.download_images()

	def download_images(self):
		self.path = './galleries/{}'.format(self.asset_code)
		if not os.path.exists(self.path):
			os.makedirs(self.path)
		counter = 0
		for url in self.gallery_links:
			counter += 1
			data = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 )'})
			with open('{}/{}.jpg'.format(self.path, counter), 'wb') as img:
				try:
					img.write(urlopen(data).read())
				except:
					pass


if __name__ == "__main__":
	if not os.path.exists('./galleries'):
		os.makedirs('./galleries')
	main_url = input('ENTER URL: ')
	user = input('Database user: ')
	password = getpass('Database password: ')
	D = DotProperty_scraper(main_url, user, password)
	D.run()