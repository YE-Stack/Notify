from django.shortcuts import render, redirect
from django.http import HttpResponse

from firebase_admin import db
from twilio.rest import Client
from Notify.settings import local_credentials

twilio_client = Client(local_credentials.twilio_auth[0], local_credentials.twilio_auth[1])

def listener(event):
	print(event.event_type)
	print(event.path)
	print(event.data)
	if event.data == None:
		return
	message = "Your Associate has sent something"
	twilio_client.messages.create(from_=local_credentials.twilio_sms_contact, body=message, to=local_credentials.web_contact)
	twilio_client.messages.create(from_="whatsapp:" + local_credentials.twilio_contact, body=message, to="whatsapp:" + local_credentials.web_contact)

db.reference('/mobile').listen(listener)

# Create your views here.

def home_view(request):
	if request.method == 'GET':
		mobile_db = db.reference('/mobile')
		webuser_db = db.reference('/webuser')
		mobile_data = mobile_db.get()
		webuser_data = webuser_db.get()
		output = None
		m = None
		s = None
		if mobile_data != "":
			m = int(mobile_data['number'])
			s = mobile_data['text']
		if mobile_data != "" and webuser_data != "":
			result_db = db.reference('/result')
			n = int(webuser_data['number'])
			t = webuser_data['text']
			output = s + ' ' + t + ' ' + str(m + n)
			mobile_db.set("")
			webuser_db.set("")
			result_db.set(output)

			message = "Your Associate has responded"
			twilio_client.messages.create(from_=local_credentials.twilio_sms_contact, body=message, to=local_credentials.mobile_contact)
			twilio_client.messages.create(from_="whatsapp:" + local_credentials.twilio_contact, body=message, to="whatsapp:" + local_credentials.mobile_contact)
		return render(request, 'root.html', {"output": output, "input_number": str(m), "input_text": s})
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