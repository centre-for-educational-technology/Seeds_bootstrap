from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import translation
from django.shortcuts import redirect
from django.core.paginator import Paginator
from register import forms as reg_forms
from django.contrib.sessions.models import Session
from .models import Scenario, TechGeneration, TechStorage, Impact, ScenarioLocation, Project
from .models import EnergySupply, EnergyTransmission, Vote, UserScenario, Electrification
import pandas as pd
import pprint as pp
import json

# param configurations
param_config = {'battery': {'max': 0.0444797482359873, 'min': 2.6183049409038122e-08},
                'bio': {'max': 1.0009737770934894, 'min': 4.134278090390732e-06},
                'climate_change': {'max': 338832867477.77576, 'min': 2264742966.7965508},
                'fossil_depletion': {'max': 112827098948.31766, 'min': 650723782.6809278},
                'human_toxicity': {'max': 1474318376277.4277, 'min': 761711160.4220799},
                'hydro_run_of_river': {'max': 1.6155, 'min': 1.6155},
                'id': {'max': 260.0, 'min': 0.0},
                'import': {'max': 0.1561112495614454, 'min': 0.0003012119877652},
                'index': {'max': 0, 'min': 0},
                'infra': {'max': 1.0, 'min': 0.1881200008807587},
                'land_occupation': {'max': 36406755938.34204, 'min': 369864152.73830664},
                'marine_toxicity': {'max': 212202658532.00342, 'min': 28266978.716299444},
                'metal_depletion': {'max': 1126183171754.4175, 'min': 48075986.27911644},
                'open_field_pv': {'max': 121.84232420443843, 'min': 2.231546741630743},
                'pace': {'max': 13.096833998642731, 'min': 3.729211861614511},
                'power': {'max': 159.63839465280677, 'min': 40.8581235544374},
                'roof_mounted_pv': {'max': 31.87839696159167, 'min': 0.0006874053401419},
                'storage': {'max': 6.303784879568456, 'min': 5.898367317341074},
                'wind_offshore': {'max': 12.2881549166774, 'min': 0.003085515351798},
                'wind_onshore': {'max': 44.36655376398457, 'min': 1.5571043872453}}


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
    projects = Project.objects.all()
    return render(request, 'project_page.html', {'projects': projects})


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

        print('Metal:', metal_min, metal_max)

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
        print('community objects:', len(scenarios_community))
        scenarios_power = scenarios_community.filter(
            power_capacity__range=(power_min, power_max))
        print('power objects:', len(scenarios_power))
        scenarios_storage = scenarios_power.filter(
            storage_capacity__range=(storage_min, storage_max))
        print('storage objects:', len(scenarios_storage))
        scenarios_implementation = scenarios_storage.filter(
            implementation_pace__range=(implementation_min, implementation_max))
        print('impl objects:', len(scenarios_implementation))
        scenarios_import = scenarios_implementation.filter(
            import_dependency__range=(import_min, import_max)).order_by('id')

        scenarios_land = scenarios_import.filter(
            land_occupation__range=(land_min, land_max)).order_by('id')
        print('land objects:', len(scenarios_land))
        scenarios_metal = scenarios_land.filter(
            metal_depletion__range=(metal_min, metal_max)).order_by('id')
        print('metal objects:', len(scenarios_metal))
        scenarios_human = scenarios_metal.filter(
            human_toxicity__range=(human_min, human_max)).order_by('id')
        print('human objects:', len(scenarios_human))
        scenarios_climate = scenarios_human.filter(
            climate_change__range=(climate_min, climate_max)).order_by('id')

        # scenarios_implementation = scenarios_storage
        paginator = Paginator(scenarios_climate, 20, orphans=3)
        page_obj = paginator.get_page(1)
        page_range = list(paginator.get_elided_page_range(1))
        print('Final objects:', len(scenarios_climate))
        return render(request, 'show_results.html', {'page_obj': page_obj, 'page_range': page_range})
    else:
        locations = ScenarioLocation.objects.all()
        return render(request, 'param_selection.html', {'locations': locations})


def get_scenario_details(scenario_id):
    data = {}
    scenario = Scenario.objects.get(id=scenario_id)
    tech_sto = TechStorage.objects.all().filter(scenario=scenario)
    tech_gen = TechGeneration.objects.all().filter(scenario=scenario)
    impact = Impact.objects.all().filter(scenario=scenario)
    energy = EnergySupply.objects.all().filter(scenario=scenario)
    electrification = Electrification.objects.all().filter(scenario=scenario)
    transmission = EnergyTransmission.objects.all().filter(scenario=scenario)

    data['bio_fuel'] = scenario.bio_fuel
    data['import_dependency'] = scenario.import_dependency
    data['storage'] = {}
    data['generation'] = {}
    data['impact'] = {}
    data['energy'] = {}
    data['electrification'] = {}
    data['transmission'] = {}

    # data for bar chart of power generation
    bar_chart_data = []

    total_hydro = 0

    total_generation = 0
    for ob in tech_gen:
        data['generation'][ob.technology_type] = ob.energy_generation
        total_generation += ob.energy_generation
        trace = {
            "y": ['Power'],
            "x": [int(ob.energy_generation)],
            "name": ob.technology_type,
            "type": 'bar',
            "orientation": 'h'
        }
        bar_chart_data.append(trace)
        if 'hydro_' in ob.technology_type:
            total_hydro += ob.energy_generation

    data['power_bar_data'] = bar_chart_data

    pie_chart_data = {}
    pie_values = {}

    total_storage = 0

    for ob in tech_sto:
        data['storage'][ob.technology_type] = ob.energy_storage
        if ob.energy_storage in pie_values.keys():
            pie_values[ob.technology_type] += float(ob.energy_storage)
        else:
            pie_values[ob.technology_type] = float(ob.energy_storage)

        total_storage += ob.energy_storage

    pie_chart_data['labels'] = list(pie_values.keys())
    pie_chart_data['values'] = list(pie_values.values())
    # data manipulation to create half pie
    count_storage_tech = len(pie_chart_data['labels'])
    sum_storage = sum(pie_chart_data['values'])

    markers = COLOR_CODES[:count_storage_tech] + ['white']

    # pie_chart_data['values'] = [item/count_storage_tech for item in pie_chart_data['values']]
    pie_chart_data['values'].append(float(pie_chart_data['values'][0]))
    pie_chart_data['labels'].append('a')
    pie_chart_data['markers'] = markers

    data['power_pie_data'] = pie_chart_data

    for ob in impact:
        data['impact'][ob.technology_type] = {'land_occupation': ob.land_occupation,
                                              'marine_toxicity': ob.marine_toxicity,
                                              'human_toxicity': ob.human_toxicity,
                                              'metal_depletion': ob.metal_depletion,
                                              'fossil_depletion': ob.fossil_depletion}

    total_supply = 0
    for ob in energy:
        data['energy']['technology_type'] = ob.energy_supply
        total_supply += ob.energy_supply

    total_electrification = 0
    for ob in electrification:
        data['electrification']['type'] = ob.carriers_type
        data['electrification']['value'] = ob.electrification_rate
        total_electrification += ob.electrification_rate

    total_transmission = 0
    for ob in transmission:
        data['transmission']['from'] = ob.from_location
        data['transmission']['to'] = ob.to_location
        data['transmission']['transmission'] = ob.transmission_capacity
        total_transmission += ob.transmission_capacity

    data['total_storage'] = total_storage
    data['total_supply'] = total_supply
    data['total_electrification'] = total_electrification
    data['total_transmission'] = total_transmission
    data['total_hydro'] = total_hydro
    data['total_generation'] = total_generation
    if scenario.roof_mounted_pv:
        roof = scenario.roof_mounted_pv
    else:
        roof = 0
    if scenario.open_field_pv:
        open = scenario.open_field_pv
    else:
        open = 0
    data['total_pv'] = roof + open

    if scenario.wind_onshore:
        onshore = scenario.wind_onshore
    else:
        onshore = 0

    if scenario.wind_offshore:
        offshore = scenario.wind_offshore
    else:
        offshore = 0
    data['total_wind'] = onshore + offshore

    return data


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


def compare(request):
    scenario_id_1 = 18
    scenario_id_2 = 27
    template_data1 = get_sankey_data(scenario_id_1)
    template_data2 = get_sankey_data(scenario_id_2)
    return render(request, 'compare_scenario.html', {'template_data1': template_data1,
                                                     'template_data2': template_data2})


def inspect(request, scenario_id):
    template_data = get_sankey_data(scenario_id)

    if request.method == 'POST':
        scenario = Scenario.objects.get(id=scenario_id)
        label = request.POST['label']
        user = request.user
        project = Project.objects.get(id=request.session['project'])
        obj = UserScenario.objects.create(
            submitted_user=user, label=label, project=project, scenario=scenario)
        print('Object saved', obj)
        request.session['selected_location'] = str(select_location)
        messages.success(request, "Scenario has been added to your portfolio")
        return render(request, 'inspect_scenario.html', template_data)
    else:
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


def vote(request, selection, scenario):
    project_obj = Project.objects.get(id=request.session['project'])
    response = True if selection == 'up' else False
    submitted_user = request.user
    scenario_obj = Scenario.objects.get(id=scenario)

    obj = Vote(project=project_obj, response=response,
               submitted_user=submitted_user, scenario=scenario_obj)
    obj.save()
    messages.success(request, "Your vote has been saved")
    return redirect('inspect', scenario_id=scenario)


def portfolio(request, project_id):
    request.session['project'] = project_id

    scenarios = UserScenario.objects.all().filter(submitted_user=request.user)

    return render(request, 'portfolio.html', {'scenarios': scenarios})
