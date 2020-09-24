from django.shortcuts import render
from home.dash_apps.finished_apps.engine import get_data


# Create your views here.

def index(request):
    context = {
        'total_confirmed': get_data('total_world_confirmed'),
        'total_active': get_data('total_world_active'),
        'total_recovered': get_data('total_world_recovered'),
        'total_deaths': get_data('total_world_deaths'),

    }
    return render(request, 'index.html',context)
    
def india(request):
     context = {
        'total_confirmed': get_data('total_confirmed'),
        'total_active': get_data('total_active'),
        'total_recovered': get_data('total_recovered'),
        'total_deaths': get_data('total_deaths'),

    }
     return render(request, 'india.html', context)

def testing_labs(request):
    context = {}
    return render(request, 'testing_labs.html', context)

def about(request):
    return render(request, 'about.html')