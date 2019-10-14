from bs4 import BeautifulSoup
import concurrent.futures
import threading
import os
import requests
import time
from Girl import Girl
import random

#import urllib3
#import urllib.request
#import sys
#from pympler import muppy
#from multiprocessing.dummy import Pool as ThreadPool

class Bridesbay():
	'''Класс, реализующий парсинг сайта https://bridesbay.com/
	:param maxWorkers:int: Количество потоков
	:param max_workersPhoto:int: Количество потоков в которые скачиваются фотографии одной девушки
	:param headers:set: Set of headers
	:param proxy:set: Set of proxys'''
	def __init__(self, maxWorkers, max_workersPhoto, headers, proxy):		# maxWorkers - количество потоков, max_workersPhoto - количество потоков в которые скачиваются фотографии одной девушки
		
		self.lock = threading.RLock()		# мьютекс
		self.maxWorkers = maxWorkers
		self.max_workersPhoto = max_workersPhoto
		self.headers = headers
		self.proxy = proxy
		self.dictIdGirl={}			# словарь: Id - Girl
		self.pageCounter=1
		self.BridesbayFolder = r'Parsed_data\BridesbayFolder' 
		self.weAreWorking = True


	def AddGirl(self, key, value):				# потокобезопасное добавление гёрлы в словарь
		'''Потокобезопасное добавление гёрлы в словарь
		:param key:string: ключ
		:param value:Girl: значение'''
		with self.lock:
			self.dictIdGirl[key] = value

		# Отсюда начинается парсинг сайта
	def StartParse(self):
		'''Начинает парсить сайт bridesbay.com'''
		print("Bridesbay parser is started")	
		Girl.headers = self.headers
		if not os.path.exists(self.BridesbayFolder):
			os.makedirs(self.BridesbayFolder)			# создание папки
		#with ThreadPool(self.maxWorkers) as executor:	
		with concurrent.futures.ThreadPoolExecutor(max_workers=self.maxWorkers) as executor:
			while self.weAreWorking:
				url = "https://bridesbay.com/women-list/page" + str(self.pageCounter)				
				soup = self.GetSoup(url)	
				errorPage = len(soup.select("div.error_404"))
				if errorPage==0:		# без ошибки
					girlBlock = ()
					girlBlock = soup.select("div.girlGalleryContainerBlock-4-item-receptacle")		# получили list элементов tag					
						# запускаем потоки нахрен!
					try:
						executor.map(self.ParseGirlTagInThread, girlBlock)	
						self.pageCounter+=1
						print("\r\n\r\n\r\nPAGES: " + str(self.pageCounter) + "\r\n\r\n\r\n")
						#print(str(len(muppy.get_objects())))

					except Exception as e:
						print ("\r\n\r\n\r\n*************    ОШИБКА !!!    **************\r\n")
						print(e.__class__)
						print("\r\n" + e.__doc__ + "\r\n" + e.__str__())
						print(str(self.pageCounter))
						time.sleep(0.1)	
						#print(str(len(muppy.get_objects())))
				else:		# ошибка
					break

	def StopParse(self):
		self.weAreWorking = False

		# Метод, отправляемый в поток
	def ParseGirlTagInThread(self, girlTag):
		"""Метод, работающий в отдельном потоке
		:param girlTag: объект тег BeautifulSoup 
		"""	
		ID = girlTag.select("div.id")
		id = ID[0].string						# получили строку вида: User ID: 484969
		id=id.split(':')[1].strip()
		if id in self.dictIdGirl:
			return
		else:
			girlName = girlTag.select("a.name")[0].text
			girlAge = girlTag.select("span.age-c")[0].select("span.value")[0].text
			girlUrl ='https://bridesbay.com' + girlTag.find('a').get('href')
			self.ParseGirl(id, girlUrl, girlName, girlAge)

	def ParseGirl (self, id, url, name, age):
		soup = self.GetSoup(url)
		profileData = soup.select("div.girlGalleryProfile-data")
		span = profileData[0].findAll("span")

		country =	self.FindTextInTags(span, "Country:")
		city =	self.FindTextInTags(span, "City:")
		marital_status = self.FindTextInTags(span, "Marital status:")
		children = self.FindTextInTags(span, "Children:")
		height = self.FindTextInTags(span, "Height:")
		weight = self.FindTextInTags(span, "Weight:")
		eyeColor = self.FindTextInTags(span, "Eye color:")
		hairColor = self.FindTextInTags(span, "Hair color:")
		bodyType = self.FindTextInTags(span, "Body type")
		religion = self.FindTextInTags(span, "Religion:")
		education = self.FindTextInTags(span, "Education:")
		smoke = self.FindTextInTags(span, "Smoke:")
		drink = self.FindTextInTags(span, "Drink:")
		englishLevel = self.FindTextInTags(span, "English level:")	
		occupation =	self.FindTextInTags(span, "Occupation:")	 

		rightCol = soup.select("div.right-col")
		titles = rightCol[0].select("div.title")
		aboutMyself = self.FindTextInTags(titles, "About myself")
		aboutMyPartner = self.FindTextInTags(titles, "About my partner")
		hobbies = self.FindTextInTags(titles, "Hobbies")
		ageCriteria = self.FindTextInTags(titles, "Age criteria")
		datingGoal = self.FindTextInTags(titles, "Dating goal")

		photoBlockSoup = soup.find(True, {'class':['block-receptacle', 'photo']})
		photoMainURL = 'https://bridesbay.com' + photoBlockSoup.select('a.photo-main')[0].get('href')

		photoList = photoBlockSoup.findAll(rel="girlGalleryProfile-photo")
		photoPholder=[]
		for photo in photoList:
			photoPholder.append('https://bridesbay.com' + photo.find('img').get('src')) 	

		girl = Girl(id, url, name, age, country, city, marital_status, children, height, weight, eyeColor, hairColor, bodyType, religion, education, smoke, drink, englishLevel, occupation, aboutMyself, aboutMyPartner, hobbies, ageCriteria, datingGoal, photoMainURL, photoPholder)
		girl.SaveToFolder(self.BridesbayFolder, self.max_workersPhoto)
		self.AddGirl(id, girl)

		print('Girl ' + girl.name + ' parsed')

		# получение тега по УРЛ
	def GetSoup(self, url):
		print("Start get HTTP")
		html = requests.get(url, headers=random.sample(self.headers, 1)[0] ).text 		#Fetch HTML Page
		print("Get HTTP")
		return BeautifulSoup(html, 'html.parser')

	def FindTextInTags(self, tags, text):
		'''Пример: tags=<span>Country:</span>, находит текст Ukraine в следующем теге, если text="Country:" <div class="row-odd"><span>Country:</span> Ukraine</div>'''
		for tag in tags:
			if tag.text == text:
				return tag.next_sibling.strip()

	def SaveAllGirls(self):
		for girl in self.dictIdGirl.values():
			girl.SaveToFolder(self.BridesbayFolder, self.max_workersPhoto)
