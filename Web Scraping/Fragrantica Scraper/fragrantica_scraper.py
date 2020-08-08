import os
import csv
import requests
from selenium import webdriver
from urllib.request import Request, urlopen
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Scraper:

	def __init__(self):

		#chromedriver path
		self.path = './chromedriver.exe'
		#chromedriver options
		self.chrome_options = Options()
		self.chrome_options.add_argument("--headless")
		#main url
		#https://www.fragrantica.com/search/?dizajner=Alkemia%20Perfumes&spol=female
		self.url = input('Enter url: ')
		#list of urls of the perfumes
		self.url_list = []
		#get html
		self.driver = webdriver.Chrome(self.path, options=self.chrome_options)
		self.driver.get(self.url)
		if not os.path.exists('./gallery'):
					os.makedirs('./gallery')

	def run(self):
		self.get_urls()
		self.scrape()


	def get_urls(self):
		#button to show more products
		button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[3]/div/div/div/div/div/button')))
		clicks_counter = 0
		#clicks to show more products and get the urls - limited to 1000

		if button.get_attribute('disabled') != None:
			button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[3]/div/div/div/div/div/button')))
			for x in range(1, 30 + 1):
				try:
					product = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="main-content"]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[3]/div/div/div/span/div[{}]/div[2]/p[1]/a'.format(x))))
					product_url = product.get_attribute('href')
					if product_url.startswith('https'):
						self.url_list.append(product_url)
				except:
					break
		while button.get_attribute('disabled') == None:
			clicks_counter += 1
			button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[3]/div/div/div/div/div/button')))
			for x in range((clicks_counter - 1)*30 + 1 , clicks_counter*30 + 1):
				try:
					product = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="main-content"]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[3]/div/div/div/span/div[{}]/div[2]/p[1]/a'.format(x))))
					product_url = product.get_attribute('href')
					if product_url.startswith('https'):
						self.url_list.append(product_url)
				except:
					break
			button.click()
		print('Products found: ', len(self.url_list))
		self.driver.quit()

	def scrape(self):
		for url in self.url_list:
			try:
				self.driver = webdriver.Chrome(self.path, options=self.chrome_options)
				self.driver.get(url)
				#title
				title = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="col1"]/div/div/h1/span'))).text
				brand = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="col1"]/div/div/p/span[1]/span/a/span'))).text
				#main accords
				main_accords = {}
				for x in range(1, 10):
					try:
						accord = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="prettyPhotoGallery"]/div[1]/div[{}]/span'.format(2*x)))).text
						width  = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="prettyPhotoGallery"]/div[1]/div[{}]/div'.format(2*x)))).get_attribute('style')
						width = width.split(';')[0][7:-2]
						main_accords[accord] = width
					except:
						break
				#diagram result
				love = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="clsloveD"]'))).get_attribute('style')
				love = love.split(';')[1][9:-2]

				like = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="clslikeD"]'))).get_attribute('style')
				like = like.split(';')[1][9:-2]

				dislike = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="clsdislikeD"]'))).get_attribute('style')
				dislike = dislike.split(';')[1][9:-2]

				winter = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="clswinterD"]'))).get_attribute('style')
				winter = winter.split(';')[1][9:-2]

				spring = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="clsspringD"]'))).get_attribute('style')
				spring = spring.split(';')[1][9:-2]

				summer = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="clssummerD"]'))).get_attribute('style')
				summer = summer.split(';')[1][9:-2]

				autumn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="clsautumnD"]'))).get_attribute('style')
				autumn = autumn.split(';')[1][9:-2]

				day = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="clsdayD"]'))).get_attribute('style')
				day = day.split(';')[1][9:-2]

				night = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="clsnightD"]'))).get_attribute('style')
				night = night.split(';')[1][9:-2]
				diagram = {'love':love, 'like':like, 'dislike':dislike, 
							'winter':winter, 'spring':spring, 'summer':summer,
							 'autumn':autumn, 'day':day, 'night':night}
				main_notes = {}
				for x in range(1, 20):
					try:
						note = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="userMainNotes"]/div[{}]/img'.format(x)))).get_attribute('alt')
						note_number = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="userMainNotes"]/div[{}]/span'.format(x)))).text
						main_notes[note] = note_number
					except:
						break
				rating = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="col1"]/div/div/div[6]/p/span[1]'))).text
				rating_votes = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="col1"]/div/div/div[6]/p/span[3]'))).text
				description = ''
				for x in range(1,20):
					try:
						description += WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="col1"]/div/div/div[4]/p[{}]'.format(x)))).text + ' '
					except:
						break

				longevity = {}
				for x in range(1,10):
					try:
						longevity_text = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="col1"]/div/div/div[8]/div[1]/div/table/tbody/tr[{}]/td[1]'.format(x)))).text
						longevity_number = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="col1"]/div/div/div[8]/div[1]/div/table/tbody/tr[{}]/td[2]'.format(x)))).text
						longevity[longevity_text] = longevity_number
					except:
						break

				sillage = {}
				for x in range(1,10):
					try:
						sillage_text = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="col1"]/div/div/div[8]/div[2]/table/tbody/tr/td/table/tbody/tr[{}]/td[1]'.format(x)))).text
						sillage_number = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="col1"]/div/div/div[8]/div[2]/table/tbody/tr/td/table/tbody/tr[{}]/td[2]'.format(x)))).text
						sillage[sillage_text] = sillage_number
					except:
						break
				image_url = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="mainpicbox"]/img'))).get_attribute('src')
				local_path = './gallery/{}'.format(brand)
				if not os.path.exists(local_path):
					os.makedirs(local_path)
				data = Request(image_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 )'})
				with open('{}/{}.jpg'.format(local_path, title), 'wb') as img:
					try:
						img.write(urlopen(data).read())
					except:
						pass
				self.write_csv(title, brand, main_accords, diagram, main_notes, rating, 
							rating_votes, description, longevity, sillage, image_url, url)
				self.driver.quit()
			except (KeyboardInterrupt, SystemExit):
				raise
			except:
				print('Unable to download: ', url)


	def write_csv(self, title, brand, main_accords,diagram, 
						main_notes, rating, rating_votes, 
						description, longevity, sillage, image_url, url):
		if not os.path.isfile('./fragrantica.csv'):
			with open('fragrantica.csv', 'w', newline='') as file:
				csv_titles =  ['title', 'brand', 'main_accords', 'diagram', 'main_notes', 'rating', 
							'rating_votes', 'description', 'longevity', 'sillage', 'image_url']
				writer = csv.writer(file)
				writer.writerow(csv_titles)
		with open('fragrantica.csv', 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([title, brand, main_accords, diagram, main_notes, rating, 
							rating_votes, description, longevity, sillage, image_url])
		print('New perfume downloaded: ', url)
		print('Title: ', title)
		print('Brand: ', brand)
		print('Main accords: ', main_accords)
		print('Diagram:', diagram)
		print('Main notes: ', main_notes)
		print('Rating: ', rating)
		print('Rating votes: ', rating_votes)
		print('Description: ', description)
		print('Longevity: ', longevity)
		print('Sillage: ', sillage)
		print('Image url: ', image_url)
		

if __name__ == '__main__':
	s = Scraper()
	s.run()