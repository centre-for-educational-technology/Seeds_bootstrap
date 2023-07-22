from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import translation
from django.shortcuts import redirect
from django.core.paginator import Paginator

from .models import Scenario

def index(request):
    return render(request,'index.html',{})

def selection(request):
    POWER_MIN = 13.24
    POWER_MAX = 135.09

    STORAGE_MIN = 5.7
    STORAGE_MAX = 6.3

    if request.method == 'POST':
        #fetching energy systems params
        #print('value:{} type:{}'.format(request.POST['power_0'],type(request.POST['power_0'])))
        power_min = POWER_MIN * float(request.POST['power_0'])
        power_max = POWER_MAX * float(request.POST['power_1'])
        storage_min = STORAGE_MIN * float(request.POST['storage_0'])
        storage_max = STORAGE_MAX * float(request.POST['storage_1'])
        community_min = request.POST['community_0']
        community_max = request.POST['community_1']
        implementation_min = float(request.POST['implement_0'])
        implementation_max = float(request.POST['implement_1'])
        import_min = request.POST['import_0']
        import_max = request.POST['import_1']

        #fetching impact controls params
        land_min = request.POST['land_0']
        land_max = request.POST['land_1']
        metal_min = request.POST['metal_0']
        metal_max = request.POST['metal_1']
        human_min = request.POST['human_0']
        human_max = request.POST['human_1']
        #climate_min = request.POST['climate_0']
        #climate_max = request.POST['climate_1']

        #fetching energy technologies params
        photo_roof_min = request.POST['photo-roof_0']
        photo_roof_max = request.POST['photo-roof_1']
        photo_open_field_min = request.POST['photo-open-field_0']
        photo_open_field_max = request.POST['photo-open-field_1']
        hydrogen_min = request.POST['hydrogen_0']
        hydrogen_max = request.POST['hydrogen_1']

        hydro_river_min = request.POST['hydro-river_0']
        hydro_river_max = request.POST['hydro-river_1']
        hydro_pumped_min = request.POST['hydro-pumped_0']
        hydro_pumped_max = request.POST['hydro-pumped_1']
        hydro_reservoir_min = request.POST['hydro-reservoir_0']
        hydro_reservoir_max = request.POST['hydro-reservoir_1']
        
        wind_on_shore_min = request.POST['wind-on-shore_0']
        wind_on_shore_max = request.POST['wind-on-shore_1']
        wind_off_shore_min = request.POST['wind-off-shore_0']
        wind_off_shore_max = request.POST['wind-off-shore_1']

        transmission_min = request.POST['transmission_0']
        transmission_max = request.POST['transmission_1']
        bio_min = request.POST['bio_0']
        bio_max = request.POST['bio_1']
        battery_min = request.POST['battery_0']
        battery_max = request.POST['battery_1']
        
        print('Power min:{} max:{}'.format(power_min,power_max))

        print('Hyodro-river min:{} max:{}'.format(hydro_river_min,hydro_river_max))
        print('wind-on-shore min:{} max:{}'.format(wind_on_shore_min,wind_on_shore_max))
        print('Human min:{} max:{}'.format(human_min,human_max))

        # Scale of parameters in database
        scenarios_community = Scenario.objects.all().filter(community_infrastructure__range=(community_min,community_max))
        scenarios_power = scenarios_community.filter(power_capacity__range=(power_min,power_max))
        scenarios_storage = scenarios_power.filter(storage_capacity__range=(storage_min,storage_max))
        scenarios_implementation = scenarios_power.filter(implementation_pace__range=(implementation_min,implementation_max))
        scenarios_import = scenarios_implementation.filter(import_dependency__range=(import_min,import_max))


        techs_gen = TechGeneration.objects()

        #scenarios_implementation = scenarios_storage

        paginator = Paginator(scenarios_import, 10, orphans=3)
        total_obs = len(scenarios_import)
        
        page_obj = paginator.get_page(1)

        page_range = list(paginator.get_elided_page_range(1))
        return render(request,'show_results.html',{'page_obj':page_obj,'page_range':page_range})

    else:
        return render(request,'param_selection.html',{})

def aboutus(request):
    return render(request,'index.html',{})

def portfolio(request):
    return render(request,'portfolio.html')
