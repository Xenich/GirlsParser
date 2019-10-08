from bs4 import BeautifulSoup
import urllib3
import urllib.request
import concurrent.futures
import threading
import os
import requests
import time
import sys
from pympler import muppy
from multiprocessing.dummy import Pool as ThreadPool

class Bridesbay():

	def __init__(self, maxWorkers, max_workersPhoto, headers):		# maxWorkers - количество потоков, max_workersPhoto - количество потоков в которые скачиваются фотографии одной девушки
		self.lock = threading.RLock()		# мьютекс
		self.maxWorkers = maxWorkers
		self.max_workersPhoto = max_workersPhoto
		self.headers = headers
		self.dictIdGirl={}			# словарь: Id - Girl
		self.pageCounter=1
		self.BridesbayFolder = r'Parsed_data\BridesbayFolder' 
		self.weAreWorking = True

		# потокобезопасное добавление гёрлы в словарь
	def AddGirl(self, key, value):
		with self.lock:
			self.dictIdGirl[key] = value

		# Отсюда начинается парсинг сайта
	def StartParse(self):
		'''Начинает парсить сайт bridesbay.com'''
		print("Bridesbay parser is started")	

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
						print("Pages: " + str(self.pageCounter) + "\r\n")
						#print(str(len(muppy.get_objects())))

					except Exception as e:
						print ("\r\n*************    ОШИБКА !!!    **************\r\n")
						print(e.__class__)
						print( "\r\n" + e.__doc__ + "\r\n" + e.__str__())
						print(str(self.pageCounter))
						time.sleep(0.1)	
						#print(str(len(muppy.get_objects())))
				else:		# ошибка
					break

	def StopParse(self):
		self.weAreWorking = False

		# Метод, отправляемый в поток
	def ParseGirlTagInThread(self, girlTag):	
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
		girl = Girl()	
		self.AddGirl(id, girl)
		girl.id = id
		girl.URL = url	
		girl.name = name
		girl.age = age
		soup = self.GetSoup(url)
		profileData = soup.select("div.girlGalleryProfile-data")
		span = profileData[0].findAll("span")

		girl.country =	self.FindTextInTags(span, "Country:")
		girl.city =	self.FindTextInTags(span, "City:")
		girl.marital_status = self.FindTextInTags(span, "Marital status:")
		girl.children = self.FindTextInTags(span, "Children:")
		girl.height = self.FindTextInTags(span, "Height:")
		girl.weight = self.FindTextInTags(span, "Weight:")
		girl.eyeColor = self.FindTextInTags(span, "Eye color:")
		girl.hairColor = self.FindTextInTags(span, "Hair color:")
		girl.bodyType = self.FindTextInTags(span, "Body type")
		girl.religion = self.FindTextInTags(span, "Religion:")
		girl.education = self.FindTextInTags(span, "Education:")
		girl.smoke = self.FindTextInTags(span, "Smoke:")
		girl.drink = self.FindTextInTags(span, "Drink:")
		girl.englishLevel = self.FindTextInTags(span, "English level:")	
		girl.occupation =	self.FindTextInTags(span, "Occupation:")	 

		rightCol = soup.select("div.right-col")
		titles = rightCol[0].select("div.title")
		girl.aboutMyself = self.FindTextInTags(titles, "About myself")
		girl.aboutMyPartner = self.FindTextInTags(titles, "About my partner")
		girl.hobbies = self.FindTextInTags(titles, "Hobbies")
		girl.ageCriteria = self.FindTextInTags(titles, "Age criteria")
		girl.datingGoal = self.FindTextInTags(titles, "Dating goal")

		photoBlockSoup = soup.find(True, {'class':['block-receptacle', 'photo']})
		girl.photoMainURL = 'https://bridesbay.com' + photoBlockSoup.select('a.photo-main')[0].get('href')
		self.dictIdGirl[id] = girl
		photoList = photoBlockSoup.findAll(rel="girlGalleryProfile-photo")
		for photo in photoList:
			girl.photoPholder.append('https://bridesbay.com' + photo.find('img').get('src')) 
		girl.SaveToFolder(self.BridesbayFolder, self.max_workersPhoto)
		print('Girl ' + girl.name + ' parsed')

		# получение тега по УРЛ
	def GetSoup(self, url):
		print("Start get HTTP")
		html = requests.get(url).text 		#Fetch HTML Page
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


class Girl():
	def __init__(self):
		self.id=""
		self.URL = ""
		self.name=""
		self.age=""
		self.country=""
		self.city=""
		self.marital_status=""
		self.children=""
		self.height=""
		self.weight=""
		self.eyeColor=""
		self.hairColor=""
		self.bodyType=""
		self.religion=""
		self.education=""
		self.smoke=""
		self.drink=""
		self.englishLevel=""	
		self.occupation=""	
		self.aboutMyself="" 
		self.aboutMyPartner=""
		self.hobbies=""
		self.ageCriteria=""
		self.datingGoal=""
		self.photoMainURL=""
		self.photoPholder=[]
	
	def SaveToFolder(self, folder, max_workersPhoto):
		info =  "ID:" + str(self.id) + ". Name: " + str(self.name)+"; age: " + str(self.age) + "; country: " + str(self.country) + "; city: " + str(self.city) + "\r\n"
		info += "Marital status: " + str(self.marital_status) + "; children: " + str(self.children) + "; height: " + str(self.height) + "; weight: " + str(self.weight) + "; eyeColor: " + str(self.eyeColor) + "; hairColor: " + str(self.hairColor) + "\r\n" 
		info += "Body type : " + str(self.bodyType) + "; religion: " + str(self.religion) + "; education: " + str(self.education) + "; smoke: " + str(self.smoke) + "; drink: " + str(self.drink) + "; english level: " + str(self.englishLevel) + "; occupation: " + str(self.occupation) + "\r\n"
		info += "About myself:\r\n"
		info += str(self.aboutMyself) + "\r\n\r\n"
		info += "About my partner:\r\n"
		info += str(self.aboutMyPartner) + "\r\n\r\n"
		info += "Hobbies: " + str(self.hobbies) + "; age criteria: " + str(self.ageCriteria) + "; dating goal: " + str(self.datingGoal) + "\r\n"
		info += "Main photo URL: " + str(self.photoMainURL) + "\r\n"
		info += "URL: " + str(self.URL) + "\r\n"
		girlFolder = folder + "\\" + self.id
		if not os.path.exists(girlFolder):
			os.makedirs(girlFolder)	
		f=open(girlFolder + "\\"+ self.id +".txt", 'wt')	
		f.write(info)	
		f.close()
			# сохраняем фотографии
		photosList = []			# список кортежей типа [(photoUrl1, Path1), (photoUrl2, Path2), (photoUrl3, Path3), ... ]
		photosList.append((self.photoMainURL, girlFolder + "\\" + self.id +"_main.jpg"))		# добавляем в список кортеж главной фотографии
		counter=1			# счётчик фотографий. будет использоваться в названии файла
		for photoUrl in self.photoPholder:
			photoCortege = (photoUrl, girlFolder + "\\" + self.id +"_" + str(counter) + ".jpg")
			photosList.append(photoCortege)
			counter+=1		
		with concurrent.futures.ThreadPoolExecutor(max_workersPhoto) as executor:		# реализация сохранения фотографий с использованием многопоточности
			executor.map(self.SaveImageFromTuple, tuple(photosList))

		'''		# реализация сохранения фотографий без потоков (по очереди)
		for photoUrl in self.photoPholder:
			self.SaveImage(photoUrl, girlFolder + "\\" + self.id +"_" + str(counter) + ".jpg")
			counter+=1
		'''

	def SaveImage(self, URL, path):
		img =	requests.get(URL)				# получили бинарные данные
		with open(path, 'wb') as f:
			f = open(path, "wb")
			f.write(img.content)
			print(self.id + ": PhotoSaved")

	def SaveImageFromTuple(self, tup):		# tup - tuple вида (photoUrl, path)
		img =	requests.get(tup[0])				# получили бинарные данные
		with open(tup[1], 'wb') as f:
			f = open(tup[1], "wb")
			f.write(img.content)
			print(self.id + ": PhotoSaved")