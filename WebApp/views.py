from django.shortcuts import render, redirect
from django.http import HttpResponse

from Notify.settings import twilio_session
from credentials import twilio_contact, mobile_contact, web_contact
from firebase_admin import db
import requests

twilio_api_link = "https://api.twilio.com/2010-04-01/Accounts/AC05527c10148eab4a7742610285965992/Messages.json"

def listener(event):
	print(event.event_type)
	print(event.path)
	print(event.data)
	whatsapp_message = {
		"To": web_contact,
		"From": twilio_contact,
		"Body": "Your friend has messaged you :)"
	}
	twilio_session.post(twilio_api_link, data=whatsapp_message)

db.reference('/mobile').listen(listener)

# Create your views here.

def home_view(request):
	if request.method == 'GET':
		mobile_db = db.reference('/mobile')
		webuser_db = db.reference('/webuser')
		mobile_data = mobile_db.get()
		webuser_data = webuser_db.get()
		output = None
		if mobile_data != "" and webuser_data != "":
			result_db = db.reference('/result')
			m = int(mobile_data['number'])
			n = int(webuser_data['number'])
			s = mobile_data['text']
			t = webuser_data['text']
			output = s + ' ' + t + ' ' + str(m + n)
			mobile_db.set("")
			webuser_db.set("")
			result_db.set(output)

			whatsapp_message = {
				"To": mobile_contact,
				"From": twilio_contact,
				"Body": "Hi, your friend has responded to your request :)"
			}
			twilio_session.post(twilio_api_link, data=whatsapp_message)
		return render(request, 'root.html', {"output": output})
	elif request.method == 'POST':
		webuser_db = db.reference('/webuser')
		r = request.POST
		m = int(r['number'])
		s = r['text']
		obj = webuser_db.set({
			"number": str(m),
			"text": s
		})
		print(m, s, obj)
		return redirect('/')
	else:
		return HttpResponse(status=405)