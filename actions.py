from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
from rasa_core.events import Restarted
from collections import OrderedDict
import zomatopy
import json
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import requests
from bs4 import BeautifulSoup


class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'

	def run(self, dispatcher, tracker, domain):
		config = {"user_key": "38ea3bc52cb3ef1015ead4b3fa7c3dc2"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		location_detail = zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat = d1["location_suggestions"][0]["latitude"]
		lon = d1["location_suggestions"][0]["longitude"]
		cuisines_dict = {'bakery': 5, 'chinese': 25, 'cafe': 30, 'italian': 55, 'biryani': 7, 'north indian': 50,
						 'south indian': 85}
		results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5)
		d = json.loads(results)
		response = ""
		if d['results_found'] == 0:
			response = "no results"
		else:
			for restaurant in d['restaurants']:
				response = response + "Found " + restaurant['restaurant']['name'] + " in " + \
						   restaurant['restaurant']['location']['address'] + "\n"

		dispatcher.utter_message("-----" + response)
		return [SlotSet('location', loc)]


class ActionRestaurantsRating(Action):
	def name(self):
		return 'action_restaurantRating'

	def run(self, dispatcher, tracker, domain):
		# initialize to store all ids falling in a category.
		id_list = []


		config = {"user_key": "38ea3bc52cb3ef1015ead4b3fa7c3dc2"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		#returns the list of IDs of restaurants nearby
		location_detail = zomato.get_location(loc, 1)
		print(location_detail)
		d1 = json.loads(location_detail)
		lat = d1["location_suggestions"][0]["latitude"]
		lon = d1["location_suggestions"][0]["longitude"]
		cuisines_dict = {'bakery': 5, 'chinese': 25, 'cafe': 30, 'italian': 55, 'biryani': 7, 'north indian': 50,
						 'south indian': 85}
		results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5)
		d = json.loads(results)
		print(d)
		response = ""
		if d['results_found'] == 0:
			response = "no results"
			dispatcher.utter_message("-----" + response)
		else:
			for restaurant in d['restaurants']:
				rest_id = (restaurant['restaurant']['R']['res_id'])
				id_list.append(rest_id)
		dispatcher.utter_message(str(id_list))


		#iterates through each id
		for each_id in id_list:
			rest_details=zomato.get_restaurant(int(each_id))
			dispatcher.utter_message("-----" + rest_details)
		#	id_list.append(rest_details["user_rating"])

		dispatcher.utter_message("-----" + location_detail)

		return [SlotSet('location', loc)]


class ActionBudgetRestaurant(Action):
	def name(self):
		return 'action_budget'

	def filterRestaurantBasedOnBudget(self, userbudget, allRestaurants):
		rangeMin = 0
		rangeMax = 100000

		if userbudget.isdigit():
			price = int(userbudget)

			if price == 1:
				rangeMax = 300
			elif price == 2:
				rangeMin = 301
				rangeMax = 700
			elif price == 3:
				rangeMin = 701
			elif price < 300:
				rangeMax = 299
			elif price < 301 and price >= 700:
				rangeMin = 301
				rangeMax = 700
			else:
				rangeMin = 701
		else:
			# default budget
			rangeMin = 301
			rangeMax = 700

		index = 0
		count = 0
		response = ""
		global result_final
		result_final = ""

		for restaurant in allRestaurants:
			count=count+1

			avg_c_2 = restaurant['restaurant']['average_cost_for_two']

			if avg_c_2 <= rangeMax and avg_c_2 >= rangeMin:

				res = restaurant['restaurant']['currency'] + str(
					restaurant['restaurant']['average_cost_for_two']) + " " + res + "\n"
				if (index < 5):
					response = response + res

				if (index < 10):
					result_final = result_final + res
				index = index + 1

		if index == 0:
			response = "Oops! no restaurant found for this query. " + " search results = " + str(count)
		elif index < 5:

			response = response + "Please search in higher budget range."
		elif index < 10:
			result_final = result_final + "For more results please search in higher budget range."

		return response


	def run(self, dispatcher, tracker, domain):
		config = {"user_key": "38ea3bc52cb3ef1015ead4b3fa7c3dc2"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		budget = tracker.get_slot('budget')

		location_detail = zomato.get_location(loc, 1)

		d1 = json.loads(location_detail)
		lat = d1["location_suggestions"][0]["latitude"]
		lon = d1["location_suggestions"][0]["longitude"]
		cuisines_dict = {'chinese': 25, 'italian': 55, 'north indian': 50, 'south indian': 85, 'Mexican': 73, 'American': 1}
		results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5)

		d = json.loads(results)
		response = ""

		if d['results_found'] == 0:
			response = "Sorry, we didn't find any results for this query."
		else:
			# dispatcher.utter_message(str(d))
			response = self.filterRestaurantBasedOnBudget(budget, d['restaurants'])

		dispatcher.utter_message(str(response))
		return [SlotSet('location', loc)]





class ActionSearchCity(Action):
	def name(self):
		return 'action_city'
	
	def run(self, dispatcher, tracker, domain):
		url="https://en.wikipedia.org/wiki/Classification_of_Indian_cities"
		r = requests.get(url,verify=False)
		soup = BeautifulSoup(r.text, "html.parser")
		
		tier_cities=list(map(lambda x:x.text.lower(),soup.find('table',class_='wikitable').find_all('a')))
		loc = tracker.get_slot('location')
		if loc is not None:
			if loc.lower() in tier_cities:
				return[SlotSet('location',loc)]
			else:
				dispatcher.utter_message("Sorry, Service Unavailable in this area.")
				return[SlotSet('location',None)]
		else:
			dispatcher.utter_message("Location is invalid. Kindly try again")
			return[SlotSet('location', None)]
			
class ActionSearchCuisine(Action):
	def name(self):
		return 'action_search_cuisine'
		
	def run(self, dispatcher, tracker, domain):
		list_cuisine = ["Chinese","Mexican","American","Italian","South Indian","North Indian"]
		cuisine = tracker.get_slot('cuisine')
		if cuisine is not None:
			if cuisine.lower() in list_cuisine:
				return[SlotSet('cuisine',cuisine)]
			else:
				dispatcher.utter_message("Cuisine is not yet listed. Would you love to try some other cusine")
				return[SlotSet('cuisine',None)]
		else:
			dispatcher.utter_message("Kinly check the entered Cuisine and try again")
			return[SlotSet('cuisine', None)]
			
class ActionSearchBudget(Action):
	def name(self):
		return 'action_search_budget'
		
	def run(self, dispatcher, tracker, domain):
		cost_queried = tracker.get_slot('budget')
		if cost_queried == 'less than 300' or cost_queried == 'lesser than 300' or ("cheap" in cost_queried) or ("pocket friendly" in cost_queried):
			return[SlotSet('budget', 'low')]
		elif cost_queried == 'more than 700'or cost_queried == 'greater than 700' or ("costly" in cost_queried):
			return[SlotSet('budget', 'high')]
		else:
			return[SlotSet('budget', 'mid')]
			
class ActionValidateEmail(Action):
	def name(self):
		return 'action_validate_email'
		
	def run(self, dispatcher, tracker, domain):
		pattern = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
		email_check = tracker.get_slot('email')
		if email_check is not None:
			if re.search("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",email_check):
				return[SlotSet('email',email_check)]
			else:
				dispatcher.utter_message("Sorry this is not a valid email. please check for typing errors")
				return[SlotSet('email',None)]
		else:
			dispatcher.utter_message("Sorry I could not understand the email address which you provided? Please provide again")
			return[SlotSet('email', None)]			
	

		
class ActionRestarted(Action): 	
    def name(self): 		
        return 'action_restarted' 	
    def run(self, dispatcher, tracker, domain): 
        return[Restarted()] 