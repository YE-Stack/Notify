from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home_view(request):
	if request.method == 'GET':
		return render(request, 'root.html',{"output":"	hello"})
	else:
		return HttpResponse(status=405)