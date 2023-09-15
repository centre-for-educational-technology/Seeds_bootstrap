from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import translation
from django.shortcuts import redirect
from django.core.paginator import Paginator
from register import forms as reg_forms
from django.contrib.sessions.models import Session
from .models import Scenario, TechGeneration, TechStorage, Impact, ScenarioLocation
import pandas as pd
import pprint as pp
import json

# param configurations
param_config = {'id': {'min': 0.0, 'max': 260.0},
                'infra': {'min': 0.1881200008807587, 'max': 1.0},
                'pace': {'min': 3.729211861614511, 'max': 13.096833998642731},
                'import': {'min': 0.0003012119877652, 'max': 0.1561112495614454},
                'power': {'min': 40.8581235544374, 'max': 159.63839465280677},
                'storage': {'min': 5.898367317341074, 'max': 6.303784879568456},
                'bio': {'min': 4.134278090390732e-06, 'max': 1.0009737770934894},
                'battery': {'min': 2.6183049409038122e-08, 'max': 0.0444797482359873},

                'wind_onshore': {'min': 1.5571043872453, 'max': 44.36655376398457},
                'wind_offshore': {'min': 0.003085515351798, 'max': 12.2881549166774},
                'open_field_pv': {'min': 2.231546741630743, 'max': 121.84232420443844},
                'roof_mounted_pv': {'min': 0.0006874053401419, 'max': 31.87839696159167},
                'hydro_run_of_river': {'min': 1.6155, 'max': 1.6155},
                'fossil_depletion': {'min': 369864152.7383066, 'max': 36406755938.34204},
                'human_toxicity': {'min': 369864152.7383066, 'max': 36406755938.34204},
                'land_occupation': {'min': 369864152.7383066, 'max': 36406755938.34204},
                'marine_toxicity': {'min': 369864152.7383066, 'max': 36406755938.34204},
                'metal_depletion': {'min': 369864152.7383066, 'max': 36406755938.34204},
                'climate_change': {'min': 369864152.7383066, 'max': 36406755938.34204},
                'import_dep': {'min': 0.0003012119877652, 'max': 0.1561112495614454}
                }

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


COLOR_CODES = ["rgba(31, 119, 180, 0.8)",
               "rgba(255, 127, 14, 0.8)",
               "rgba(44, 160, 44, 0.8)",
               "rgba(214, 39, 40, 0.8)",
               "rgba(148, 103, 189, 0.8)",
               "rgba(140, 86, 75, 0.8)",
               "rgba(227, 119, 194, 0.8)",
               "rgba(127, 127, 127, 0.8)",
               "rgba(188, 189, 34, 0.8)",
               "rgba(23, 190, 207, 0.8)",
               "rgba(31, 119, 180, 0.8)",
               "rgba(255, 127, 14, 0.8)",
               "rgba(44, 160, 44, 0.8)",
               "rgba(214, 39, 40, 0.8)",
               "rgba(148, 103, 189, 0.8)",
               "rgba(140, 86, 75, 0.8)",
               "rgba(227, 119, 194, 0.8)",
               "rgba(127, 127, 127, 0.8)",
               "rgba(188, 189, 34, 0.8)",
               "rgba(23, 190, 207, 0.8)",
               "rgba(31, 119, 180, 0.8)",
               "rgba(255, 127, 14, 0.8)",
               "rgba(44, 160, 44, 0.8)",
               "rgba(214, 39, 40, 0.8)",
               "rgba(148, 103, 189, 0.8)",
               "rgba(140, 86, 75, 0.8)",
               "rgba(227, 119, 194, 0.8)",
               "rgba(127, 127, 127, 0.8)",
               "rgba(188, 189, 34, 0.8)",
               "rgba(23, 190, 207, 0.8)",
               "rgba(31, 119, 180, 0.8)",
               "rgba(255, 127, 14, 0.8)",
               "rgba(44, 160, 44, 0.8)",
               "rgba(214, 39, 40, 0.8)",
               "rgba(148, 103, 189, 0.8)",
               "magenta"]


def reduce_intensity(c, intensity=.2):
    return c.replace('0.8', '0.2')


def index(request):
    form = reg_forms.LoginForm()
    return render(request, 'index.html', {'form': form})


def project_page(request):
    return render(request, 'project_page.html', {})


def rescale(value, min, max):
    range = max - min
    return min + float(value) * range


def selection(request):

    if request.method == 'POST':
        # fetching energy systems params
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

        # fetching impact controls params
        land_min = rescale(request.POST['land_0'], param_config['land_occupation']
                           ['min'], param_config['land_occupation']['max'])
        land_max = rescale(request.POST['land_1'], param_config['land_occupation']
                           ['min'], param_config['land_occupation']['max'])
        metal_min = rescale(request.POST['metal_0'], param_config['metal_depletion']
                            ['min'], param_config['metal_depletion']['max'])
        metal_max = rescale(request.POST['metal_1'], param_config['metal_depletion']
                            ['min'], param_config['metal_depletion']['max'])
        human_min = rescale(request.POST['human_0'], param_config['human_toxicity']
                            ['min'], param_config['human_toxicity']['max'])
        human_max = rescale(request.POST['human_1'], param_config['human_toxicity']
                            ['min'], param_config['human_toxicity']['max'])
        climate_min = rescale(
            request.POST['climate_0'], param_config['climate_change']['min'], param_config['climate_change']['max'])
        climate_max = rescale(
            request.POST['climate_1'], param_config['climate_change']['min'], param_config['climate_change']['max'])

        # fetching energy technologies params
        photo_roof_min = rescale(
            request.POST['photo-roof_0'], param_config['roof_mounted_pv']['min'], param_config['roof_mounted_pv']['max'])
        photo_roof_max = rescale(
            request.POST['photo-roof_1'], param_config['roof_mounted_pv']['min'], param_config['roof_mounted_pv']['max'])
        photo_open_field_min = rescale(
            request.POST['photo-open-field_0'], param_config['open_field_pv']['min'], param_config['open_field_pv']['max'])
        photo_open_field_max = rescale(
            request.POST['photo-open-field_1'], param_config['open_field_pv']['min'], param_config['open_field_pv']['max'])

        # @todo: add hydrogen in scenario table
        hydrogen_min = request.POST['hydrogen_0']
        hydrogen_max = request.POST['hydrogen_1']

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
        bio_min = request.POST['bio_0']
        bio_max = request.POST['bio_1']
        battery_min = rescale(
            request.POST['battery_0'], param_config['battery']['min'], param_config['battery']['max'])

        battery_max = rescale(
            request.POST['battery_1'], param_config['battery']['min'], param_config['battery']['max'])

        # Location
        selected_location = request.POST['location']

        # print('Power min:{} max:{}'.format(power_min,power_max))
        # print('Hyodro-river min:{} max:{}'.format(hydro_river_min,hydro_river_max))
        # print('wind-on-shore min:{} max:{}'.format(wind_on_shore_min,wind_on_shore_max))
        # print('Human min:{} max:{}'.format(human_min,human_max))

        # Scale of parameters in database
        scenarios_community = Scenario.objects.all().filter(
            community_infrastructure__range=(community_min, community_max))
        print('Tota objects:', len(scenarios_community))
        scenarios_power = scenarios_community.filter(
            power_capacity__range=(power_min, power_max))
        print('Tota objects:', len(scenarios_power))
        scenarios_storage = scenarios_power.filter(
            storage_capacity__range=(storage_min, storage_max))
        print('Tota objects:', len(scenarios_storage))
        scenarios_implementation = scenarios_storage.filter(
            implementation_pace__range=(implementation_min, implementation_max))

        scenarios_import = scenarios_implementation.filter(
            import_dependency__range=(import_min, import_max)).order_by('id')

        scenarios_land = scenarios_import.filter(
            land_occupation__range=(land_min, land_max)).order_by('id')
        scenarios_metal = scenarios_land.filter(
            metal_depletion__range=(land_min, land_max)).order_by('id')
        scenarios_human = scenarios_metal.filter(
            human_toxicity__range=(land_min, land_max)).order_by('id')
        scenarios_climate = scenarios_human.filter(
            climate_change__range=(land_min, land_max)).order_by('id')

        print('land objects:', len(scenarios_implementation))
        # scenarios_implementation = scenarios_storage
        paginator = Paginator(scenarios_climate, 20, orphans=3)
        total_obs = len(scenarios_import)
        page_obj = paginator.get_page(1)
        page_range = list(paginator.get_elided_page_range(1))
        print('Final objects:', len(scenarios_import))
        return render(request, 'show_results.html', {'page_obj': page_obj, 'page_range': page_range})
    else:
        locations = ScenarioLocation.objects.all()
        return render(request, 'param_selection.html', {'locations': locations})


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


def inspect(request, scenario_id):

    template_data = get_sankey_data(scenario_id)
    return render(request, 'inspect_scenario.html', template_data)


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


def portfolio(request):
    return render(request, 'portfolio.html')
