import urllib2
from bs4 import BeautifulSoup
import datetime
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import mysql.connector
import smtplib

#Install the mysql server and above packages
#After installation of above packages, Run this script,
#to run this script type 'python scrap.py' in the downloaded folder

sender = "****@gmail.com"
password = "******" #set the password
 
def create_db(): #creates the Database and Required Table
	mydb = mysql.connector.connect(
  	host="localhost",
  	user="yourusername",
  	passwd="yourpassword",
  	database="mydatabase"
	)
	mycursor = mydb.cursor()
	mycursor.execute("CREATE TABLE users (email_address VARCHAR(50), series VARCHAR(50))")

#create_db()
while(True):
	def send_email(schedule, email_address,email_string): #function to send send email to the input email_address(s)
		receivers = email_address
		message = """From: From Shivam <gera.shivam@gmail.com>
		To: To Person  """+email_address+""" 
		Subject: Schedule
		"""+email_string
		#try:
		message = """From: From Person <from@fromdomain.com>
		To: To Person <to@todomain.com>
		Subject: SMTP e-mail test

		"""+email_string+"""
		"""
   		smtpObj = smtplib.SMTP('smtp.gmail.com',587)
   		smtpObj.starttls()
   		smtpObj.login(sender, password)
   		smtpObj.sendmail(sender, receivers, message)         
  		print "Successfully sent email"
		#except smtplib.SMTPException:
   		#print "Error: unable to send email"

	def nav_webpage(tv_show): #Navigate the Chrome browser and returns the current URL with respect to tv show 
		try:

			driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver')
			driver.get('https://www.imdb.com')
			search_box = driver.find_element_by_id('navbar-query')
			search_box.send_keys(tv_show)
			submit_button = driver.find_element_by_id('navbar-submit-button')
			submit_button.click()
			select_text = driver.find_element_by_link_text(tv_show.title())
			select_text.click()
			episodes_link = driver.find_element_by_partial_link_text('Episode Guide')
			episodes_link.click()
			select = Select(driver.find_element_by_id("bySeason"))
			selectLen = len(select.options)
			select.select_by_index(selectLen-1)
			time.sleep(3)
			return driver.current_url
		except:
			return "Error"



	def get_dates(tv_show): #scraps the page for the returned URL by nav_webpage and returns the status of tv show
		date_page = nav_webpage(tv_show)
		page = urllib2.urlopen(date_page)
		soup = BeautifulSoup(page, 'html.parser')
		dates = [ i.text for i in soup.find_all('div',{'class':'airdate'})]
		present_date = datetime.datetime.today().strftime('%Y-%m-%d')
		try:
			for j in range(len(dates)):
				x = dates[j].strip()
				if(len(x)==4):
					return x
				if(x==None or x==''):
					return None
				if x:
					try:
						x = datetime.datetime.strptime(x,'%d %b. %Y')
					except:
						x = datetime.datetime.strptime(x,'%d %b %Y')
					x = x.strftime('%Y-%m-%d')
					if(x>present_date):
						return x
					elif (j==len(dates)-1):
						return "finished"
					else:
						continue
		except:
			return "Error: Date not found"


	def user_query(): #input by user
		email_address = raw_input("Enter Email Address: ")
		user_query = raw_input("Enter tv series(s) seprated by comma(,):")
		list_query = user_query.split(",")
		email_string = ''
		for i in list_query:
			sql = "INSERT INTO users (email_address, series) VALUES (%s, %s)"
			val = (email_address, i)
			mycursor.execute(sql, val)
			mydb.commit()
			schedule = get_dates(i)
			if(schedule==None):
				schedule = "To be Announced"
			print(schedule+" for "+i)
			email_string = email_string+"TV series name:  "+i
			email_string = email_string+ "\nstatus : "+ schedule+ "\n"
		send_email(schedule, email_address, email_string)




	user_query()