import requests
import concurrent.futures
import os
import random

class Girl():
	headers = []
	def __init__(self, id, URL, name, age, country, city, marital_status, children, height, weight, eyeColor, hairColor, 
	bodyType, religion, education, smoke, drink, englishLevel, occupation, aboutMyself, aboutMyPartner, hobbies, ageCriteria, datingGoal, photoMainURL, photoPholder):
		self.id=id
		self.URL = URL
		self.name=name
		self.age=age
		self.country=country
		self.city=city
		self.marital_status=marital_status
		self.children=children
		self.height=height
		self.weight=weight
		self.eyeColor=eyeColor
		self.hairColor=hairColor
		self.bodyType=bodyType
		self.religion=religion
		self.education=education
		self.smoke=smoke
		self.drink=drink
		self.englishLevel=englishLevel
		self.occupation=occupation
		self.aboutMyself=aboutMyself
		self.aboutMyPartner=aboutMyPartner
		self.hobbies=hobbies
		self.ageCriteria=ageCriteria
		self.datingGoal=datingGoal
		self.photoMainURL=photoMainURL
		self.photoPholder=photoPholder
	
	def SaveToFolder(self, folder, max_workersPhoto):
		'''Сохранение информации о человеке
		:param folder:string: Папка назначения
		:param max_workersPhoto:int: Количество потоков в которые скачиваются фотографии одного человека'''
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
		'''Сохранение фотографии
		:param tup:tuple: кортеж вида (photoUrl, path)'''
		img =	requests.get(tup[0], headers=random.sample(Girl.headers, 1)[0])				# получили бинарные данные
		with open(tup[1], 'wb') as f:
			f = open(tup[1], "wb")
			f.write(img.content)
			print(self.id + ": PhotoSaved")