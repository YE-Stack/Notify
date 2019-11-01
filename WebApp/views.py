from django.shortcuts import render, redirect
from django.http import HttpResponse

from firebase_admin import db
from twilio.rest import Client
from Notify.settings import local_credentials

from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError

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
			expo_token = db.reference('/token').get()
			output = s + ' ' + t + ' ' + str(m + n)
			mobile_db.set("")
			webuser_db.set("")
			result_db.set(output)

			message = "Your Associate has responded"
			try:
				send_push_message(expo_token['token'], message, extra=None)
			except:
				print("Could not send push notification")
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

def send_push_message(token, message, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        rollbar.report_exc_info(
            extra_data={'token': token, 'message': message, 'extra': extra})
        raise self.retry(exc=exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        from notifications.models import PushToken
        PushToken.objects.filter(token=token).update(active=False)
    except PushResponseError as exc:
        # Encountered some other per-notification error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'push_response': exc.push_response._asdict(),
            })
        raise self.retry(exc=exc)