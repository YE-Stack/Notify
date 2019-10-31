from django.shortcuts import render, redirect
from django.http import HttpResponse

from Notify.settings import firebase_db

# Create your views here.

def home_view(request):
	if request.method == 'GET':
		mobile_data = firebase_db.child('mobile').get().val()
		webuser_data = firebase_db.child('webuser').get().val()
		output = None
		if mobile_data != "" and webuser_data != "":
			m = int(mobile_data['number'])
			n = int(webuser_data['number'])
			s = mobile_data['text']
			t = webuser_data['text']
			output = s + ' ' + t + ' ' + str(m + n)
			firebase_db.child('mobile').set("")
			firebase_db.child('webuser').set("")
			firebase_db.child('result').set(output)
		return render(request, 'root.html', {"output": output})
	elif request.method == 'POST':
		r = request.POST
		m = int(r['number'])
		s = r['text']
		obj = firebase_db.child('webuser').set({
			"number": str(m),
			"text": s
		})
		print(m, s, obj)
		return redirect('/')
	else:
		return HttpResponse(status=405)