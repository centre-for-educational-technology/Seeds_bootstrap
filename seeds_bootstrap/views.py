from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.models import model_to_dict
from register import views as rv
from register.forms import RegisterForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import translation
from django.shortcuts import redirect
from django.core.paginator import Paginator
from register import forms as reg_forms
from django.contrib.sessions.models import Session
from .models import Scenario, TechGeneration, TechStorage, ScenarioLocation, Project, QueryParameters, ActivityLog
from .models import EnergySupply, EnergyTransmission, Vote, UserScenario, Electrification
import pandas as pd
import pprint as pp
from django.conf import settings
from urllib.parse import unquote
from django.http import JsonResponse
from django.utils.translation import (
    check_for_language, get_language,
)
LANGUAGE_SESSION_KEY = '_language'
# location mapping
location_mapping = {'PRT-1_1': 'Aveiro',
                    'PRT-3_1': 'Beja',
                    'PRT-4_1': 'Braga',
                    'PRT-6_1': 'Castelo Branco',
                    'PRT-7_1': 'Coimbra',
                    'PRT-10_1': 'Guarda',
                    'PRT-11_1': 'Leiria',
                    'PRT-12_1': 'Lisboa',
                    'PRT-14_1': 'Portalegre',
                    'PRT-15_1': 'Porto',
                    'PRT-18_1': 'Viana do Castelo',
                    'PRT-19_1': 'Vila Real',
                    'PRT-20_1': 'Viseu',
                    'PRT-5_1': 'Bragança',
                    'PRT-8_1': 'Évora',
                    'PRT-16_1': 'Santarém',
                    'PRT-17_1': 'Setúbal',
                    'PRT-9_1': 'Faro',
                    'PRT_1': 'Norte',
                    'PRT_2': 'Sul'}
# param configurations
param_config = {'battery': {'max': 0.0444797482359873, 'min': 2.6183049409038122e-08},
                'bio': {'max': 1.0009737770934894, 'min': 4.134278090390732e-06},
                'freshwater_eutrophication': {'max': 1447977268.6580737,
                                              'min': 40539809.033321954},
                'global_warming': {'max': 3550705057804.7417, 'min': 89357470400.92726},
                'hydro_run_of_river': {'max': 1.6155, 'min': 1.6155},
                'import': {'max': 0.2, 'min': 0},
                'import_dep': {'max': 0.1561112495614454, 'min': 0.0003012119877652},
                'infra': {'max': 1.0, 'min': 0},
                'land_occupation': {'max': 216513993115, 'min': 20280814757},
                'open_field_pv': {'max': 125, 'min': 0},
                'pace': {'max': 13.096833998642731, 'min': 3.729211861614511},
                'power': {'max': 159.63839465280677, 'min': 40.8581235544374},
                'roof_mounted_pv': {'max': 26, 'min': 0},
                'scenario': {'max': 260.0, 'min': 0.0},
                'storage': {'max': 6.303784879568456, 'min': 5.898367317341074},
                'surplus_ore': {'max': 655458310608.2251, 'min': 9926424157.968464},
                'water_consumption': {'max': 61979898600.96115, 'min': 859061013.8176432},
                'wind_offshore': {'max': 13, 'min': 0},
                'wind_onshore': {'max': 45, 'min': 0},
                'hydrogen': {'max': 8, 'min': 0}}

POWER_TECHS = ['chp_biofuel_extraction',
               'chp_hydrogen',
               'chp_methane_extraction',
               'chp_wte_back_pressure',
               'electrolysis',
               'existing_pv',
               'existing_wind',
               'hydro_reservoir',
               'hydro_run_of_river',
               'open_field_pv',
               'pumped_hydro',
               'wind_onshore',
               'battery',
               'ccgt',
               'roof_mounted_pv',
               'wind_offshore']

POWER_GEN_TECHS = ['chp_biofuel_extraction',
               'chp_hydrogen',
               'chp_methane_extraction',
               'chp_wte_back_pressure',
               'existing_pv',
               'existing_wind',
               'hydro_reservoir',
               'hydro_run_of_river',
               'open_field_pv',
               'wind_onshore',
               'roof_mounted_pv',
               'wind_offshore']

SYSTEM_BALANCE_TECHS = ['electrolysis','ccgt','transmission','pumped_hydro','battery']
SYSTEM_BALANCE_LABELS = {'electrolysis':'Electrolysers','ccgt':'Syngas CCGT turbine',
                         'transmission':'Transmission','pumped_hydro':'Pumped Hydro','battery':'Battery'}
SYSTEM_BALANCE_COLORS = {'electrolysis':'#A708A4','ccgt':'#DDB3C8',
                         'transmission':'#FDB735',
                         'pumped_hydro':'#0097EC','battery':'#73E600'}

POWER_TECHS_LABELS = {'chp_biofuel_waste':'CHP Biofuel & Waste',
               'chp_hydrogen':'CHP Hydrogen',
               'chp_methane_extraction':'CHP Methane',
               'electrolysis':'Electrolysis',
               'hydro_reservoir':'Hydro Reservoir',
               'hydro_run_of_river':'Hydro River',
               'solar':'Solar',
               'pumped_hydro':'Pumped Hyrdo',
               'wind':'Wind',
               'hydro':'Hydro',
               'battery':'Battery',
               'ccgt':'Syngaz CCGT turbine',}

POWER_TECHS_COLORS = {'chp_biofuel_waste':'#C78281',
                      'chp_biofuel_extraction':'#C78281',
               'chp_hydrogen':'#08A4A7',
               'chp_methane_extraction':'#B14F7E',
               'chp_wte_back_pressure':'#A4A708',
               'electrolysis':'#A708A4',
               'existing_pv':'#894E07',
               'solar':'#894E07',
               'wind':'#5B814A',
               'existing_wind':'#5B814A',
               'hydro_reservoir':'#00169F',
               'hydro_run_of_river':'#0021EC',
               'open_field_pv':'#F3911D',
               'pumped_hydro':'#0097EC',
               'wind_onshore':'#73A25E',
               'battery':'#73E600',
               'ccgt':'#DDB3C8',
               'roof_mounted_pv':'#FDB735',
               'wind_offshore':'#69B578'}


def documentation(request):
    return render(request, 'documentation.html')


def reduce_intensity(c, intensity=.2):
    return c.replace('0.8', '0.2')


def create_log_entry(project_id, actor, verb, object, notes):
    try: 
        project = Project.objects.get(id=project_id)
        object = ActivityLog(project=project, actor=actor.email,
                         verb=verb, object=object, notes=notes)
        object.save()
    except:
        return

def get_mapdata(scenario_id):
    solar = {}
    wind = {}
    scenario = Scenario.objects.get(id=scenario_id)
    tech_gen = TechGeneration.objects.all().filter(scenario=scenario)
    for tech_ob in tech_gen:
        if 'wind' in tech_ob.technology_type:
            if tech_ob.location.location in wind.keys():
                wind[tech_ob.location.location] += float(
                    tech_ob.energy_generation)
            else:
                wind[tech_ob.location.location] = float(
                    tech_ob.energy_generation)

        if 'pv' in tech_ob.technology_type:
            if tech_ob.location.location in solar.keys():
                solar[tech_ob.location.location] += float(
                    tech_ob.energy_generation)
            else:
                solar[tech_ob.location.location] = float(
                    tech_ob.energy_generation)
    map_data = {}
    map_data['solar'] = {}
    map_data['solar']['z'] = []
    map_data['solar']['locations'] = []
    map_data['solar']['text'] = []

    for key, value in solar.items():
        map_data['solar']['locations'].append(key)
        map_data['solar']['z'].append(value)
        map_data['solar']['text'].append(location_mapping[key])

    map_data['wind'] = {}
    map_data['wind']['z'] = []
    map_data['wind']['locations'] = []
    map_data['wind']['text'] = []
    for key, value in wind.items():
        map_data['wind']['locations'].append(key)
        map_data['wind']['z'].append(value)
        map_data['wind']['text'].append(location_mapping[key])
    return map_data


def index(request):
    if request.method == "POST":
        if request.POST.get("form_type") == 'signup':
            email = request.POST['email']
            form = RegisterForm()
            return render(request, "sign_up.html", {"form": form, 'email': email})
        elif request.POST.get("form_type") == 'signin':
            return rv.login(request)
        else:
            return rv.register(request)
    else:
        form = reg_forms.LoginForm()
        return render(request, 'index.html', {'form': form})


def project_page(request):
    projects = Project.objects.all()
    return render(request, 'project_page.html', {'projects': projects})


def rescale(value, min, max):
    range = max - min
    return min + float(value) * range


def standardise(value, min, max):
    range = max - min
    return min - float(value) / range


def standardise(value, min, max):
    range = float(max) - float(min)
    return (float(value) - float(min)) / range


def filter_scenarios(search_params,project_id):
    #@todo: filter based on project_id

    #print('------>', search_params)
    scenarios_community = Scenario.objects.all().filter(
        community_infrastructure__range=(search_params['community_min'], search_params['community_max']))
    scenarios_power = scenarios_community.filter(
        power_capacity__range=(search_params['power_min'], search_params['power_max']))
    #print('power objects:', len(scenarios_power))
    scenarios_storage = scenarios_power.filter(
        storage_capacity__range=(search_params['storage_min'], search_params['storage_max']))
    #print('storage objects:', len(scenarios_storage))
    scenarios_implementation = scenarios_storage.filter(
        implementation_pace__range=(search_params['implementation_min'], search_params['implementation_max']))
    #print('impl objects:', len(scenarios_implementation))
    scenarios_import = scenarios_implementation.filter(
        import_dependency__range=(search_params['import_min'], search_params['import_max']))
    #print('import objects:', len(scenarios_import))
    scenarios_land = scenarios_import.filter(
        land_occupation__range=(search_params['land_min'], search_params['land_max']))
    #print('land objects:', len(scenarios_land))
    scenarios_global = scenarios_land.filter(
        global_warming__range=(search_params['global_min'], search_params['global_max']))
    #print('global objects:', len(scenarios_global))
    scenarios_surplus = scenarios_global.filter(
        surplus_ore__range=(search_params['surplus_min'], search_params['surplus_max']))
    #print('surplus objects:', len(scenarios_surplus))
    scenarios_water = scenarios_surplus.filter(
        water_consumption__range=(search_params['water_min'], search_params['water_max']))
    #print('water objects:', len(scenarios_water))
    scenarios_fresh = scenarios_water.filter(
        freshwater_eutrophication__range=(search_params['fresh_min'], search_params['fresh_max']))

    scenarios_roof_pv = scenarios_fresh.filter(
        roof_mounted_pv__range=(search_params['photo_roof_min'], search_params['photo_roof_max']))
    
    # There are scenarios with nan values for pv_roof
    if (int(search_params['photo_roof_min']) == 0) and (int(search_params['photo_roof_max']== 26)):
        scenarios_roof_pv = scenarios_fresh
    #print(int(search_params['photo_roof_min']), int(search_params['photo_roof_max']))
    #print((int(search_params['photo_open_field_min']) == 0) and (int(search_params['photo_open_field_min']== 26)))
    #print('photo objects roof:', len(scenarios_roof_pv))
    
    scenarios_open_field_pv = scenarios_roof_pv.filter(
        open_field_pv__range=(search_params['photo_open_field_min'], search_params['photo_open_field_max']))
    
    if (int(search_params['photo_open_field_min']) == 0) and (int(search_params['photo_open_field_max']== 125)):
        scenarios_open_field_pv = scenarios_roof_pv 

    #print('photo objects field:', len(scenarios_open_field_pv))
    scenarios_wind_onshore = scenarios_open_field_pv.filter(
        wind_onshore__range=(search_params['wind_onshore_min'], search_params['wind_onshore_max']))
    #print(search_params['wind_onshore_min'],search_params['wind_onshore_max'])
    if (int(search_params['wind_onshore_min']) == 0) and (int(search_params['wind_onshore_max']== 45)):
        scenarios_wind_onshore = scenarios_open_field_pv

    #print('wind on objects:', len(scenarios_wind_onshore))
    scenarios_wind_offshore = scenarios_wind_onshore.filter(
        wind_offshore__range=(search_params['wind_offshore_min'], search_params['wind_offshore_max']))
    if (int(search_params['wind_offshore_min']) == 0) and (int(search_params['wind_offshore_max']== 13)):
        scenarios_wind_offshore = scenarios_wind_onshore

    #print('wind off objects:', len(scenarios_wind_offshore))
    scenarios_hydrogen = scenarios_wind_offshore.filter(
        hydrogen__range=(search_params['hydrogen_min'], search_params['hydrogen_max']))
    if (int(search_params['hydrogen_min']) == 0) and (int(search_params['hydrogen_max']== 125)):
        scenarios_open_field_pv = scenarios_roof_pv

    #print('hydrogen objects:', len(scenarios_hydrogen))
    scenarios_biofuel = scenarios_hydrogen.filter(
        bio_fuel__range=(search_params['bio_min'], search_params['bio_max']))
    if (int(search_params['photo_open_field_min']) == 0) and (int(search_params['photo_open_field_max']== 125)):
        scenarios_open_field_pv = scenarios_roof_pv

    #print('bio objects:', len(scenarios_biofuel))
    scenarios_battery = scenarios_biofuel.filter(
        battery__range=(search_params['battery_min'], search_params['battery_max'])).order_by('id')
    if (int(search_params['photo_open_field_min']) == 0) and (int(search_params['photo_open_field_max']== 125)):
        scenarios_open_field_pv = scenarios_roof_pv

    #print('battery objects:', len(scenarios_battery))
    return scenarios_battery

def get_search_params(request,project_id):
    search_params = {}
    if request.method == 'POST':
        # fetching energy systems params
        search_params = {}
        power_min = request.POST['power_0']
        power_max = request.POST['power_1']
        storage_min = request.POST['storage_0']
        storage_max = request.POST['storage_1']

        community_min = rescale(
            float(request.POST['community_0']), param_config['infra']['min'], param_config['infra']['max'])
        community_max = rescale(
            float(request.POST['community_1']), param_config['infra']['min'], param_config['infra']['max'])
        implementation_min = request.POST['implement_0']
        implementation_max = request.POST['implement_1']
        import_min = rescale(
            float(request.POST['import_0']), param_config['import']['min'], param_config['import']['max'])
        import_max = rescale(
            float(request.POST['import_1']), param_config['import']['min'], param_config['import']['max'])

        ele_heat_min = request.POST['heat_0']
        ele_heat_max = request.POST['heat_1']

        ele_road_min = request.POST['transport_0']
        ele_road_max = request.POST['transport_1']

        # search_params['project'] = project_id
        search_params['power_min'] = power_min
        search_params['power_max'] = power_max
        search_params['storage_min'] = storage_min
        search_params['storage_max'] = storage_max
        search_params['community_min'] = community_min
        search_params['community_max'] = community_max
        search_params['implementation_min'] = implementation_min
        search_params['implementation_max'] = implementation_max
        search_params['import_min'] = import_min
        search_params['import_max'] = import_max
        search_params['ele_heat_min'] = ele_heat_min
        search_params['ele_heat_max'] = ele_heat_max

        # fetching impact controls params
        land_min = rescale(request.POST['land_0'], param_config['land_occupation']
                           ['min'], param_config['land_occupation']['max'])
        land_max = rescale(request.POST['land_1'], param_config['land_occupation']
                           ['min'], param_config['land_occupation']['max'])
        global_min = rescale(request.POST['global_0'], param_config['global_warming']
                             ['min'], param_config['global_warming']['max'])
        global_max = rescale(request.POST['global_1'], param_config['global_warming']
                             ['min'], param_config['global_warming']['max'])
        water_min = rescale(request.POST['water_0'], param_config['water_consumption']
                            ['min'], param_config['water_consumption']['max'])
        water_max = rescale(request.POST['water_1'], param_config['water_consumption']
                            ['min'], param_config['water_consumption']['max'])

        fresh_min = rescale(request.POST['fresh_0'], param_config['freshwater_eutrophication']
                            ['min'], param_config['freshwater_eutrophication']['max'])
        fresh_max = rescale(request.POST['fresh_1'], param_config['freshwater_eutrophication']
                            ['min'], param_config['freshwater_eutrophication']['max'])

        surplus_min = rescale(
            request.POST['surplus_0'], param_config['surplus_ore']['min'], param_config['surplus_ore']['max'])
        surplus_max = rescale(
            request.POST['surplus_1'], param_config['surplus_ore']['min'], param_config['surplus_ore']['max'])

        search_params['land_min'] = land_min
        search_params['land_max'] = land_max
        search_params['global_min'] = global_min
        search_params['global_max'] = global_max
        search_params['water_min'] = water_min
        search_params['water_max'] = water_max
        search_params['fresh_min'] = fresh_min
        search_params['fresh_max'] = fresh_max
        search_params['surplus_min'] = surplus_min
        search_params['surplus_max'] = surplus_max

        # fetching energy technologies paramss
        photo_roof_min = rescale(
            request.POST['photo-roof_0'], param_config['roof_mounted_pv']['min'], param_config['roof_mounted_pv']['max'])
        photo_roof_max = rescale(
            request.POST['photo-roof_1'], param_config['roof_mounted_pv']['min'], param_config['roof_mounted_pv']['max'])
        photo_open_field_min = rescale(
            request.POST['photo-open-field_0'], param_config['open_field_pv']['min'], param_config['open_field_pv']['max'])
        photo_open_field_max = rescale(
            request.POST['photo-open-field_1'], param_config['open_field_pv']['min'], param_config['open_field_pv']['max'])
        #print('Photo open field min:',photo_open_field_max,photo_open_field_min)
       
        hydrogen_min = rescale(request.POST['hydrogen_0'], param_config['hydrogen']['min'], param_config['hydrogen']['max'])
        hydrogen_max = rescale(request.POST['hydrogen_1'], param_config['hydrogen']['min'], param_config['hydrogen']['max'])

        """
        hydro_river_min = request.POST['hydro-river_0']
        hydro_river_max = request.POST['hydro-river_1']
        hydro_pumped_min = request.POST['hydro-pumped_0']
        hydro_pumped_max = request.POST['hydro-pumped_1']
        hydro_reservoir_min = request.POST['hydro-reservoir_0']
        hydro_reservoir_max = request.POST['hydro-reservoir_1']
        """

        wind_on_shore_min = rescale(
            request.POST['wind-on-shore_0'], param_config['wind_onshore']['min'], param_config['wind_onshore']['max'])
        wind_on_shore_max = rescale(
            request.POST['wind-on-shore_1'], param_config['wind_onshore']['min'], param_config['wind_onshore']['max'])
        wind_off_shore_min = rescale(
            request.POST['wind-off-shore_0'], param_config['wind_offshore']['min'], param_config['wind_offshore']['max'])
        wind_off_shore_max = rescale(
            request.POST['wind-off-shore_1'], param_config['wind_offshore']['min'], param_config['wind_offshore']['max'])

        transmission_min = request.POST['transmission_0']
        transmission_max = request.POST['transmission_1']
        bio_min = rescale(
            request.POST['bio_0'], param_config['bio']['min'], param_config['bio']['max'])
        bio_max = rescale(
            request.POST['bio_1'], param_config['bio']['min'], param_config['bio']['max'])
        battery_min = rescale(
            request.POST['battery_0'], param_config['battery']['min'], param_config['battery']['max'])

        battery_max = rescale(
            request.POST['battery_1'], param_config['battery']['min'], param_config['battery']['max'])

        search_params['photo_roof_min'] = photo_roof_min
        search_params['photo_roof_max'] = photo_roof_max
        search_params['photo_open_field_min'] = photo_open_field_min
        search_params['photo_open_field_max'] = photo_open_field_max
        search_params['hydrogen_min'] = hydrogen_min
        search_params['hydrogen_max'] = hydrogen_max
        search_params['wind_onshore_min'] = wind_on_shore_min
        search_params['wind_onshore_max'] = wind_on_shore_max
        search_params['wind_offshore_min'] = wind_off_shore_min
        search_params['wind_offshore_max'] = wind_off_shore_max
        search_params['transmission_min'] = transmission_min
        search_params['transmission_max'] = transmission_max
        search_params['bio_min'] = bio_min
        search_params['bio_max'] = bio_max
        search_params['battery_min'] = battery_min
        search_params['battery_max'] = battery_max
    else:
        search_params = request.session['search_params']
    return search_params

def get_filtered_scenarios(request, project_id):
    search_params = get_search_params(request, project_id)
    scenarios_filtered = filter_scenarios(search_params,project_id)
    return scenarios_filtered


def get_scenarios_count_ajax(request):
    #@todo: add project_id in the code
    #print(request.POST)
    search_params = get_search_params(request, 1)
    scenarios_filtered = filter_scenarios(search_params,1)
    return JsonResponse({'total_scenarios': len(scenarios_filtered)})


def interface(request, project_id, starting_scenario):
    if starting_scenario == 'a':
        template = 'param_selection_a.html'
    else:
        template = 'param_selection_b.html'

    request.session['starting_scenario'] = starting_scenario

    if request.method == 'POST':
        search_params = get_search_params(request,project_id)
        request.session['search_params'] = search_params
        return redirect('show_results',project_id=project_id)
    else:
        return render(request, template, {'project': project_id})


def show_results(request, project_id):
    search_params = request.session['search_params']
    scenarios_filtered = get_filtered_scenarios(
            request, project_id)
    create_log_entry(project_id, request.user, 'submitted',
                         'search parameters', '')
    print('created log entry')
    starting_scenario = request.session['starting_scenario']
    #request.session['search_params'] = search_params
        
    return render(request, 'show_results.html', {'page_obj': scenarios_filtered,
                                                     'json_format': serializers.serialize('json', scenarios_filtered),
                                                     'project_id': project_id,
                                                     'starting_scenario':starting_scenario,
                                                      'search_params':search_params,
                                                     })


def changLang(request, lang_code):
    next = request.META.get('HTTP_REFERER')
    next = next and unquote(next)  # HTTP_REFERER may be encoded.
    #print('URL:', next)
    response = HttpResponse(status=204)
    if lang_code == 'pt':
        next = next.replace('/en/', '/pt/')
    if lang_code == 'en':
        next = next.replace('/pt/', '/en/')
    response = HttpResponseRedirect(next)
    return response


def get_saved_search(request, search_id):
    ob = model_to_dict(QueryParameters.objects.get(id=search_id))
    search_params = {}
    for key in ob:
        if key != 'sub_date' and key != 'submitted_user':
            search_params[key] = ob[key]
    scenarios_filtered = filter_scenarios(search_params)
    return render(request, 'show_results.html', {'page_obj': scenarios_filtered,
                                                 'search_params': search_params,
                                                 'json_format': serializers.serialize('json', scenarios_filtered),
                                                 'project_id': 1})


@csrf_exempt
def save_search_params(request, label):
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = {}
            data['label'] = label
            data['submitted_user'] = request.user
            for key in request.POST:
                if 'key' == 'project':
                    project = Project.objects.get(id=request.POST[key])
                else:
                    data[key] = request.POST[key]
            print(data)
            q = QueryParameters(**data)
            q.save()
        create_log_entry(1, request.user, 'saved',
                         'saved search parameters', '')

        return HttpResponse('success')
    else:
        return HttpResponse('failure')


def get_scenario_details(scenario_id):
    data = {}
    scenario = Scenario.objects.get(id=scenario_id)
    tech_sto = TechStorage.objects.all().filter(scenario=scenario)
    tech_gen = TechGeneration.objects.all().filter(scenario=scenario)
    energy = EnergySupply.objects.all().filter(scenario=scenario)
    electrification = Electrification.objects.all().filter(scenario=scenario)
    transmission = EnergyTransmission.objects.all().filter(scenario=scenario)
    data['scenario'] = scenario
    data['storage'] = {}
    data['generation'] = {}
    data['energy'] = {}
    data['electrification'] = {}
    data['transmission'] = {}

    radial_chart_r = [scenario.land_occupation, scenario.global_warming,
                      scenario.water_consumption, scenario.surplus_ore, scenario.freshwater_eutrophication]
    radial_chart_theta = ['Land Occupation', 'Global Warming',
                          'Water Consumption', 'Surplus Ore', 'FreshWater Eutrophication']
    # data for bar chart of power generation

    impact_names = [('_'.join(item.split(' '))).lower()
                    for item in radial_chart_theta]

    tmp = []
    for ind, val in enumerate(radial_chart_r):
        print(param_config[impact_names[ind]]['min'],
              param_config[impact_names[ind]]['max'])
        tmp.append(standardise(
            val, param_config[impact_names[ind]]['min'], param_config[impact_names[ind]]['max']))
        
    radial_chart_theta_acroynm = ['LOP', 'GWP',
                          'WCP', 'SOP', 'FEP']

    data['radial_r'] = tmp
    data['radial_theta'] = radial_chart_theta_acroynm

    bar_chart_data = []

    total_hydro = 0

    total_generation = 0
    for ob in tech_gen:
        # causing error due to replacing
        if ob.technology_type in data['generation']:
            data['generation'][ob.technology_type] += ob.energy_generation
        else:
            data['generation'][ob.technology_type] = ob.energy_generation
        total_generation += ob.energy_generation
        if 'hydro' in ob.technology_type:
            total_hydro += ob.energy_generation

    processed_power_gen_colors = {'solar':'#D2770B',
                              'chp_biofuel_waste':'#9B1E1D',
                              'Electricity_import':'#E6E600',
                              'hydro':'#00659F',
                              'wind':'#3F5A33',
                              'chp_hydrogen':'#08A4A7',
                              'chp_methane_extraction':'#B14F7E',}
    
    ###### Preparing final power generation data for chart
    final_generation_data = {}
    final_generation_data['wind'] = 0
    final_generation_data['solar'] = 0
    final_generation_data['chp_biofuel_waste'] = 0
    final_generation_data['hydro'] = 0

    for key, value in data['generation'].items():
        value = float(value)
        if 'existing' in key:
            continue
        
        if key in POWER_GEN_TECHS:
            if 'wind' in key:
                final_generation_data['wind'] += value
            elif 'pv' in key:
                final_generation_data['solar'] += value
            elif 'chp_bio' in key or 'chp_wte' in key:
                final_generation_data['chp_biofuel_waste'] += value
            elif 'hydro' in key:
                final_generation_data['hydro'] += value
            elif key in final_generation_data.keys():
                final_generation_data[key] += value
            else:
                final_generation_data[key] = value

    
    #print('Power gen data=====>')
    #print(final_generation_data)

    data['total_power_gen'] = 0
    for key, value in final_generation_data.items():
        trace = {
            "y": ['Power'],
            "x": [str(round(value, 2))],
            "name": POWER_TECHS_LABELS[key],
            "marker": { 'color':processed_power_gen_colors[key]},
            "type": 'bar',
            "orientation": 'h',
            "hovertemplate": '{}: {} GW <extra></extra>'.format(POWER_TECHS_LABELS[key],str(round(value, 2)))
        }
        data['total_power_gen'] += value
        bar_chart_data.append(trace)

    data['power_bar_data'] = bar_chart_data
    ################


    pie_chart_data = {}
    pie_values = {}

    total_storage = 0
    ###### Preparing final System balancing data for chart
    total_transmission = 0
    for ob in transmission:
        data['transmission']['from'] = ob.from_location
        data['transmission']['to'] = ob.to_location
        data['transmission']['transmission'] = ob.transmission_capacity
        total_transmission += ob.transmission_capacity

    system_data = {'ccgt':0,'electrolysis':0,'transmission':0,'pumped_hydro':0,'battery':0}

    for key, value in data['generation'].items():
        if key in system_data.keys():
            system_data[key] += float(value)

    # transmission represents total transmission capacity (inflow + outflow)
    system_data['transmission'] = total_transmission

    system_chart_data = []
    for key, value in system_data.items():
        trace = {
            "y": ['System Balance'],
            "x": [str(round(value, 2))],
            "name": SYSTEM_BALANCE_LABELS[key],
            "marker": { 'color':SYSTEM_BALANCE_COLORS[key]},
            "type": 'bar',
            "orientation": 'h',
            "hovertemplate": '{}: {} GW <extra></extra>'.format(SYSTEM_BALANCE_LABELS[key],str(round(value, 2)))
        }
        system_chart_data.append(trace)

    data['storage_bar_data'] = system_chart_data
    data['total_system_balance_capacity'] = sum([float(item) for item in system_data.values()])

    pie_chart_data['labels'] = list(pie_values.keys())
    pie_chart_data['values'] = list(pie_values.values())
    # data manipulation to create half pie
    count_storage_tech = len(pie_chart_data['labels'])
    sum_storage = sum(pie_chart_data['values'])

    energy, energy_data, total_supply, pie_colors = get_energy_supply(scenario_id)
    generation_labels = list(data['generation'].keys())
    generation_values = list(data['generation'].values())

    data['energy_supply_pie_labels'] = list(energy_data.keys())
    data['energy_supply_pie_values'] = list(energy_data.values())
    data['energy_supply_pie_colors'] = list(pie_colors.values())
    data['energy_supply_total'] = total_supply
    data['generation_labels'] = generation_labels
    data['generation_values'] = [float(item) for item in generation_values]
    data['power_pie_data'] = pie_chart_data

    data['energy'] = energy
    total_electrification = 0
    for ob in electrification:
        print(ob.carriers_type, ':', ob.electrification_rate)
        print(ob.carriers_type in data['electrification'].keys())
        if ob.carriers_type in data['electrification'].keys():
            data['electrification'][ob.carriers_type] += float(
                ob.electrification_rate)
        else:
            data['electrification'][ob.carriers_type] = float(
                ob.electrification_rate)

        total_electrification += ob.electrification_rate

    data['electrification']['heat_percentage'] = data['electrification']['heat'] * \
        100 / float(total_electrification)
    data['electrification']['transport_percentage'] = data['electrification']['transport'] * \
        100 / float(total_electrification)


    data['total_storage'] = total_storage
    data['total_supply'] = total_supply
    data['total_electrification'] = total_electrification
    data['total_transmission'] = total_transmission
    data['total_hydro'] = total_hydro
    data['total_generation'] = total_generation

    if 'existing_pv' in data['generation'].keys():
        exist_pv = data['generation']['existing_pv']
    else:
        exist_pv = 0

    if 'roof_pv' in data['generation'].keys():
        roof = data['generation']['roof_pv']
    else:
        roof = 0

    if 'open_field_pv' in data['generation'].keys():
        open = data['generation']['open_field_pv']
    else:
        open = 0

    data['total_pv'] = roof + open  + exist_pv

    #print('=====> Total PV:',data['total_pv'])

    data['pv_roof_percentage'] = '{:.2}'.format(roof * 100 / data['total_pv'])
    data['pv_open_percentage'] = '{:.2}'.format(open * 100 / data['total_pv'])

    if 'existing_wind' in data['generation'].keys():
        exist_wind = data['generation']['existing_wind']
    else:
        exist_wind = 0

    if 'wind_onshore' in data['generation'].keys():
        onshore = data['generation']['wind_onshore']
    else:
        onshore = 0

    if 'wind_offshore' in data['generation'].keys():
        offshore = data['generation']['wind_offshore']
    else:
        offshore = 0
    data['total_wind'] = onshore + offshore  + exist_wind
    data['wind_onshore_percentage'] = '{:.2}'.format(
        onshore * 100 / data['total_wind'])
    data['wind_offshore_percentage'] = '{:.2}'.format(
        offshore * 100 / data['total_wind'])
    
    # this is processed data with combining categories, e.g., wind on shore, offshore to wind
    data['final_generation_data'] = final_generation_data

    #print('Scenario:', model_to_dict(data['scenario']))
    #print("wind:", data['total_wind'])
    #print('generation:', data['generation'])
    #print('Final generation data:',final_generation_data)
    #print('System data:',system_data)
    return data


def get_energy_supply(scenario_id):
    scenario = Scenario.objects.get(id=scenario_id)
    supply = EnergySupply.objects.all().filter(scenario=scenario)
    energy = {}
    for ob in supply:
        if ob.technology_type in energy.keys():
            energy[ob.technology_type] += float(ob.energy_supply)
        else:
            energy[ob.technology_type] = float(ob.energy_supply)

    total_supply = '{0:.2f}'.format(sum(list(energy.values())))

    pie_energy_supply_data = {}
    pie_energy_supply_data['Solar'] = 0
    pie_energy_supply_data['Biofuel & waste'] = 0
    pie_energy_supply_data['Electricity import'] = 0
    pie_energy_supply_data['Hydro'] = 0
    pie_energy_supply_data['Wind'] = 0

    pie_energy_supply_data['Biofuel & waste'] += energy['biofuel_supply'] + \
        energy['waste_supply']
    pie_energy_supply_data['Solar'] += energy['open_field_pv'] + \
        energy['roof_mounted_pv'] + energy['existing_pv']
    pie_energy_supply_data['Electricity import'] += energy['el_import']
    pie_energy_supply_data['Hydro'] += energy['hydro_reservoir'] + \
        energy['hydro_run_of_river']
    pie_energy_supply_data['Wind'] += energy['existing_wind'] + \
        energy['wind_offshore'] + energy['wind_onshore']


    pie_energy_supply_colors = {'Solar':'#D2770B',
                              'Biofuel & waste':'#9B1E1D',
                              'Electricity import':'#E6E600',
                              'Hydro':'#00659F',
                              'Wind':'#3F5A33'}

    return energy, pie_energy_supply_data, total_supply, pie_energy_supply_colors


def get_sankey_data(scenario_id):
    available_color_code_index = 0
    data = get_scenario_details(scenario_id)

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
            'scenario': scenario_id,
            'nodes': nodes_labels, 'source': source,
            'target': target, 'value': link_value,
            'nodes_color': list(nodes_color.values()),
            'link_color': link_color}


def compare(request, sc_1, sc_2):
    sc_1 = int(sc_1)
    sc_2 = int(sc_2)
    data1 = get_scenario_details(sc_1)
    data2 = get_scenario_details(sc_2)
    mapdata1 = get_mapdata(sc_1)
    mapdata2 = get_mapdata(sc_2)

    scenarios = get_all_scenarios_impact_data(request)
    impact_a = get_impact_graph_data(scenarios, sc_1)
    impact_b = get_impact_graph_data(scenarios, sc_2)

    # log entry
    create_log_entry(1, request.user, 'compared',
                     'scenarios: {} and {}'.format(sc_1, sc_2), '')
    return render(request, 'compare_scenario.html', {'data1': data1,
                                                     'data2': data2,
                                                     'mapdata1': mapdata1,
                                                     'mapdata2': mapdata2,
                                                     'impact_a': impact_a,
                                                     'impact_b': impact_b})


def get_all_scenarios_impact_data(request):
    obs = Scenario.objects.all()
    return obs


def get_impact_graph_data(all_scenarios, current_scenario):
    impact = {}
    temp = {}
    impact_types = ['land_occupation', 'surplus_ore',
                    'freshwater_eutrophication', 'global_warming', 'water_consumption']
    for impact_type in impact_types:
        temp[impact_type] = {}
        temp[impact_type]['others'] = {}
        temp[impact_type]['self'] = {}

        impact[impact_type] = {}
        impact[impact_type]['others'] = {}
        impact[impact_type]['self'] = {}

    for scenario in all_scenarios:
        for impact_type in impact_types:
            impact_value = standardise(float(
                getattr(scenario, impact_type)), param_config[impact_type]['min'], param_config[impact_type]['max'])
            if scenario.id == current_scenario:
                temp[impact_type]['self'][scenario.id] = impact_value
            else:
                temp[impact_type]['others'][scenario.id] = impact_value

    for impact_type in impact_types:
        impact[impact_type]['others']['x'] = list(
            temp[impact_type]['others'].keys())
        impact[impact_type]['others']['y'] = list(
            temp[impact_type]['others'].values())
        impact[impact_type]['self']['x'] = list(
            temp[impact_type]['self'].keys())
        impact[impact_type]['self']['y'] = list(
            temp[impact_type]['self'].values())
    return impact


def select_starting_point(request, project_id):
    start_point_a = 45
    start_point_b = 140
    data1 = get_scenario_details(start_point_a)
    data2 = get_scenario_details(start_point_b)
    mapdata1 = get_mapdata(start_point_a)
    mapdata2 = get_mapdata(start_point_b)
    scenarios = get_all_scenarios_impact_data(request)

    impact_a = get_impact_graph_data(scenarios, start_point_a)
    impact_b = get_impact_graph_data(scenarios, start_point_b)

    return render(request, 'starting_page.html', {'data1': data1,
                                                  'data2': data2,
                                                  'mapdata1': mapdata1,
                                                  'mapdata2': mapdata2,
                                                  'impact_a': impact_a,
                                                  'impact_b': impact_b})


@staff_member_required
def get_activity_log(request):
    logs = ActivityLog.objects.all()
    print('Length:', len(logs))
    return render(request, 'activity_log.html', {'logs': logs, 'json_format': serializers.serialize('json', logs)})


def inspect(request, project_id, scenario_id):
    scenario = Scenario.objects.get(id=scenario_id)
    data = get_scenario_details(scenario_id)
    map_data = get_mapdata(scenario_id)

    scenarios = get_all_scenarios_impact_data(request)
    impact_a = get_impact_graph_data(scenarios, int(scenario_id))

    starting_scenario = request.session['starting_scenario']

    if request.method == 'POST':
        scenario = Scenario.objects.get(id=scenario_id)
        form_type = request.POST['form_type']
        if form_type == 'vote':
            selection = request.POST['vote_input']
            project_obj = Project.objects.get(id=project_id)
            response = True if selection == '1' else False
            submitted_user = request.user
            scenario_obj = Scenario.objects.get(id=scenario_id)

            obj = Vote(project=project_obj, response=response,
                       submitted_user=submitted_user, scenario=scenario_obj)
            obj.save()
            # log entry
            if response:
                create_log_entry(project_id, request.user, 'voted-positive',
                             'scenario: {}'.format(scenario_id), '')
            else:
                create_log_entry(project_id, request.user, 'voted-negative',
                             'scenario: {}'.format(scenario_id), '')
                
            messages.success(request, _("Your vote has been saved. Go back to your <a href='/results/{}'>scenario list.</a>".format(project_id)))
        else:
            user = request.user
            project = Project.objects.get(id=project_id)
            label = request.POST['label']
            obj = UserScenario.objects.create(
                submitted_user=user, label=label, project=project, scenario=scenario)
            print('Object saved', obj)
            # log entry
            create_log_entry(project_id, request.user, 'saved',
                             'scenario: {}'.format(scenario_id), '')
            messages.success(
                request, _("Scenario has been added to your portfolio. <a href = '/portfolio/saved_scenarios'>Check scenario in your portfolio.</a>"))
    else:
        create_log_entry(1, request.user, 'inspected',
                         'scenario: {}'.format(scenario_id), '')
    return render(request, 'inspect_scenario.html', {'data': data, 'project_id': project_id, 'mapdata': map_data, 'impact_a': impact_a,'starting_scenario':starting_scenario})


def select_location(request):
    locations = ScenarioLocation.objects.all()
    if request.method == 'POST':
        selected_location = request.POST['location']
        print(selected_location)
        request.session['selected_location'] = str(select_location)
        return redirect('interface')
    else:
        return render(request, 'select_location_page.html', {'locations': locations})


def aboutus(request):
    return render(request, 'index.html', {})


def vote(request, selection, scenario):
    project_obj = Project.objects.get(id=request.session['project'])
    response = True if selection == 'up' else False
    submitted_user = request.user
    scenario_obj = Scenario.objects.get(id=scenario)

    obj = Vote(project=project_obj, response=response,
               submitted_user=submitted_user, scenario=scenario_obj)
    obj.save()
    messages.success(request, _("Your vote has been saved."))
    return redirect('inspect', scenario_id=scenario)


def portfolio(request, query):
    if query in ['saved_scenarios', 'saved_searches']:
        if query == 'saved_scenarios':
            scenarios = UserScenario.objects.all().filter(submitted_user=request.user)
            return render(request, 'portfolio.html', {'scenarios': scenarios, 'title': 'Your scenarios', 'query': query})
        else:
            params = QueryParameters.objects.all().filter(submitted_user=request.user)
            return render(request, 'portfolio.html', {'scenarios': params, 'title': 'Your saved searches', 'query': query})


def portfolio_actions(request, query, command, id, label):
    if query in ['saved_scenarios', 'saved_searches']:
        if query == 'saved_scenarios':
            if command == 'update':
                object = UserScenario.objects.all().get(id=id)
                print('update :', object)
                object.label = label
                object.save()
                create_log_entry(1, request.user, 'updated',
                                 'saved scenario', '')
                messages.success(
                    request,  _('Scenario has been updated successfully !'))
            elif command == 'delete':
                UserScenario.objects.all().filter(submitted_user=request.user, id=id).delete()
                # log entry
                create_log_entry(1, request.user, 'deleted',
                                 'saved scenario entry', '')
                messages.success(
                    request,  _('Scenario has been deleted successfully !'))

            scenarios = UserScenario.objects.all().filter(submitted_user=request.user)
            return render(request, 'portfolio.html', {'scenarios': scenarios, 'title': 'Your scenarios', 'query': query})
        else:

            if command == 'update':
                object = QueryParameters.objects.all().get(id=id)
                object.label = label
                object.save()
                create_log_entry(1, request.user, 'updated',
                                 'saved search parameters entry', '')
                messages.success(
                    request,  _('Search parameter entry has been updated successfully !'))
            elif command == 'delete':
                create_log_entry(1, request.user, 'deleted',
                                 'saved search parameters entry', '')
                messages.success(
                    request,  _('Search parameter entry has been deleted successfully !'))
                QueryParameters.objects.all().filter(submitted_user=request.user, id=id).delete()

            params = QueryParameters.objects.all().filter(submitted_user=request.user)
            return render(request, 'portfolio.html', {'scenarios': params, 'title': 'Your saved searches', 'query': query})
