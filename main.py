import requests
import pyttsx3
import speech_recognition as sr
import re
from bs4 import BeautifulSoup

url = "https://www.worldometers.info/coronavirus/"

class Data:
	def __init__(self):
		page = requests.get(url)
		htmlcontent = page.content
		soup = BeautifulSoup(htmlcontent,'html.parser')
		table = soup.find('table',id="main_table_countries_today")
		headers = [heading.text.replace("Country,Other","name") for heading in table.find_all("th")]
		table_rows = [row for row in table.tbody.find_all('tr')]
		results = [{headers[index]:cell.text for index,cell in enumerate(row.find_all("td"))  } for row in table_rows]
		main_counter = soup.find_all("div",class_="maincounter-number")
		counter_list = [counter.text.strip() for counter in main_counter]
		result_total = [{'name':'Coronavirus Cases:','value':counter_list[0]}, {'name':'Deaths:','value':counter_list[1]}]
		self.data = {'total': result_total, 'country': results}

	def get_TotalCases(self):
		data = self.data['total']

		for content in data:
			if content['name'] == "Coronavirus Cases:":
				return content['value']

	def get_TotalDeaths(self):
		data = self.data['total']

		for content in data:
			if content['name'] == "Deaths:":
				return content['value']

		return "0"

	def get_country_data(self, country):
		data = self.data["country"]

		for content in data:
			if content['name'].lower() == country.lower():
				return content

		return "0"

	def get_list_of_countries(self):
		countries = []
		for country in self.data['country']:
			countries.append(country['name'].lower())

		return countries


def speak(text):
	print(text)
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

def get_audio():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""

	try:
		said = r.recognize_google(audio)
	except Exception as e:
		print("Excpetion:", str(e))

	return said.lower()


def main():
	data = Data()
	country_list = data.get_list_of_countries()
	END_PHRASE = "exit"
	END_MSG = "Thankyou for using COVI-WARE!!!"
	speak("Welcome To COVI-WARE")

	TOTAL_PATTERNS = {
					re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_TotalCases,
					re.compile("[\w\s]+ total cases"): data.get_TotalCases,
					re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_TotalDeaths,
					re.compile("[\w\s]+ total deaths"): data.get_TotalDeaths,
					re.compile("[\w\s]+ total [\w\s]+ death"): data.get_TotalDeaths,
					re.compile("[\w\s]+ total death"): data.get_TotalDeaths
					}

	COUNTRY_PATTERNS = {
						re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['TotalCases'],
                    	re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['TotalDeaths'],
                    	re.compile("[\w\s]+ death [\w\s]+"): lambda country: data.get_country_data(country)['TotalDeaths']
                    	}

	while True:
		speak("Listening...")
		text = get_audio()
		print(text)
		result = None

		for pattern, func in COUNTRY_PATTERNS.items():
			if pattern.match(text):
				words = set(text.split(" "))
				for country in country_list:
					if country in words:
						result = func(country) 
						break

		for pattern, func in TOTAL_PATTERNS.items():
			if pattern.match(text):
				result = func()
				break

		if result:
			speak(result)

		if text.find(END_PHRASE) != -1:
			speak(END_MSG)
			break

main()