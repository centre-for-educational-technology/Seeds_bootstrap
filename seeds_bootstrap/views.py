from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import translation
from django.shortcuts import redirect
from django.core.paginator import Paginator
from register import forms as reg_forms
from .models import Scenario, TechGeneration
import pandas as pd


def index(request):
    form = reg_forms.LoginForm()
    return render(request,'index.html',{'form':form})

def get_sankey_data(scenario_id):
    available_color_code_index = 0
    data = {}
    scenario = Scenario.objects.get(id=scenario_id)
    tech_sto = TechStorage.objects.all().filter(scenario=scenario)
    tech_gen = TechGeneration.objects.all().filter(scenario=scenario)
    impact = Impact.objects.all().filter(scenario=scenario)
    data['total_pv'] = scenario.roof_mounted_pv + scenario.open_field_pv
    data['total_wind'] = scenario.wind_onshore + scenario.wind_offshore
    data['bio_fuel'] = scenario.bio_fuel
    data['import_dependency'] = scenario.import_dependency
    data['storage'] = {}
    data['generation'] = {}
    data['impact'] = {}
    for ob in tech_gen:
        data['generation'][ob.technology_type] = ob.energy_generation

    for ob in tech_sto:
        data['storage'][ob.technology_type] = ob.energy_storage

    for ob in impact:
        data['impact'][ob.technology_type] = {'land_occupation': ob.land_occupation,
                                              'marine_toxicity': ob.marine_toxicity,
                                              'human_toxicity': ob.human_toxicity,
                                              'metal_depletion': ob.metal_depletion,
                                              'fossil_depletion': ob.fossil_depletion}

    nodes_labels = [item for item in data['impact'].keys()]
    nodes_labels += ['land_occupation', 'marine_toxicity',
                     'human_toxicity', 'metal_depletion',
                     'fossil_depletion', 'total']

    nodes_color = {}
    for key in nodes_labels:
        nodes_color[key] = COLOR_CODES[available_color_code_index]
        available_color_code_index += 1

    link = []

    for key in data['impact'].keys():

        link.append({'source': 'total',
                     'target': key,
                     'color': reduce_intensity(nodes_color[key]),
                     'value': sum(list(data['impact'][key].values()))
                     })

        for impact_type, impact_value in data['impact'][key].items():

            link.append({'source': key,
                         'target': impact_type,
                         'color': reduce_intensity(nodes_color[impact_type]),
                         'value': impact_value
                         })
    source = []
    target = []
    link_value = []
    link_color = []

    for l in link:
        source.append(nodes_labels.index(l['source']))
        target.append(nodes_labels.index(l['target']))
        link_value.append(float(l['value']))
        link_color.append(l['color'])

    return {'data': data,
            'nodes': nodes_labels, 'source': source,
            'target': target, 'value': link_value,
            'nodes_color': list(nodes_color.values()),
            'link_color': link_color}


def compare(request):
    scenario_id_1 = 18
    scenario_id_2 = 27
    template_data1 = get_sankey_data(scenario_id_1)
    template_data2 = get_sankey_data(scenario_id_2)
    return render(request, 'compare_scenario.html', {'template_data1': template_data1,
                                                     'template_data2': template_data2})


def inspect(request):
    scenario_id = 18
    template_data = get_sankey_data(scenario_id)
    return render(request, 'inspect_scenario.html', template_data)


def rescale(value,min,max):
    range = max - min
    return min + value * range

def selection(request):
    POWER_MIN = 13.24
    POWER_MAX = 135.09

    STORAGE_MIN = 5.7
    STORAGE_MAX = 6.3

    IMPLEMENT_MIN = 3.7
    IMPLEMENT_MAX = 13

    IMPORT_MIN = 0
    IMPORT_MAX = .15

    COMMUNITY_MIN = .18
    COMMUNITY_MAX = 1

    if request.method == 'POST':
        #fetching energy systems params

        power_min = rescale(float(request.POST['power_0']),POWER_MIN,POWER_MAX)
        power_max = rescale(float(request.POST['power_1']),POWER_MIN,POWER_MAX)
        storage_min = rescale(float(request.POST['storage_0']),STORAGE_MIN,STORAGE_MAX)
        storage_max = rescale(float(request.POST['storage_1']),STORAGE_MIN,STORAGE_MAX)
        community_min = rescale(float(request.POST['community_0']),COMMUNITY_MIN,COMMUNITY_MAX)
        community_max = rescale(float(request.POST['community_1']),COMMUNITY_MIN,COMMUNITY_MAX)
        implementation_min = rescale(float(request.POST['implement_0']),IMPLEMENT_MIN,IMPLEMENT_MAX)
        implementation_max = rescale(float(request.POST['implement_1']),IMPLEMENT_MIN,IMPLEMENT_MAX)
        import_min = rescale(float(request.POST['import_0']),IMPORT_MIN,IMPORT_MAX)
        import_max = rescale(float(request.POST['import_1']),IMPORT_MIN,IMPORT_MAX)

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

        #print('Power min:{} max:{}'.format(power_min,power_max))
        #print('Hyodro-river min:{} max:{}'.format(hydro_river_min,hydro_river_max))
        #print('wind-on-shore min:{} max:{}'.format(wind_on_shore_min,wind_on_shore_max))
        #print('Human min:{} max:{}'.format(human_min,human_max))

        # Scale of parameters in database
        scenarios_community = Scenario.objects.all().filter(community_infrastructure__range=(community_min,community_max))
        scenarios_power = scenarios_community.filter(power_capacity__range=(power_min,power_max))
        scenarios_storage = scenarios_power.filter(storage_capacity__range=(storage_min,storage_max))
        scenarios_implementation = scenarios_storage.filter(implementation_pace__range=(implementation_min,implementation_max))
        scenarios_import = scenarios_implementation.filter(import_dependency__range=(import_min,import_max)).order_by('id')


        #scenarios_implementation = scenarios_storage
        paginator = Paginator(scenarios_import, 20, orphans=3)
        total_obs = len(scenarios_import)
        page_obj = paginator.get_page(1)
        page_range = list(paginator.get_elided_page_range(1))
        print('Tota objects:',len(scenarios_import))
        return render(request,'show_results.html',{'page_obj':page_obj,'page_range':page_range})

    else:
        return render(request,'param_selection.html',{})

def aboutus(request):
    return render(request,'index.html',{})

def portfolio(request):
    return render(request,'portfolio.html')
