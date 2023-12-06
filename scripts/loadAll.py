from seeds_bootstrap.models import Scenario
from seeds_bootstrap.models import ScenarioLocation, TechGeneration
from seeds_bootstrap.models import TechStorage
from seeds_bootstrap.models import Electrification
from seeds_bootstrap.models import EnergySupply
from seeds_bootstrap.models import EnergyTransmission
from seeds_bootstrap.models import Project
from seeds_bootstrap.models import GeneratedHeat, GeneratedTransport
from seeds_bootstrap.models import FlowOut

import pandas as pd
import geopandas
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
import numpy as np
base = '/Users/htk/Documents/Work/Seeds_project/seeds_bootstrap copy/scripts'
# Data files for Scenario table

scenario = pd.read_csv(
    '{}/Scenario_with_impact_alex_data_ele_generation.csv'.format(base))
impact = pd.read_csv('{}/Impact.csv'.format(base))
tech_gen = pd.read_csv('{}/TechGeneration.csv'.format(base))
tech_sto = pd.read_csv('{}/TechStorage.csv'.format(base))
transmission = pd.read_csv('{}/energy_updated_november23/transmission_capacity.csv'.format(base))
energy_tech = pd.read_csv('{}/energy_updated_november23/energy_supply.csv'.format(base))

ele_heat = pd.read_csv(
    '{}/energy_updated_november23/electrification_rate_heat_building.csv'.format(base))
ele_road = pd.read_csv(
    '{}/energy_updated_november23/electrification_rate_road_transport.csv'.format(base))

flow_out = pd.read_csv('{}/energy_updated_november23/flow_out_sum.csv'.format(base))
build_heat = pd.read_csv('{}/energy_updated_november23/generated_building_heat.csv'.format(base))
district_heat = pd.read_csv('{}/energy_updated_november23/generated_district_heat.csv'.format(base))
road_transport = pd.read_csv('{}/energy_updated_november23/generated_road_transport.csv'.format(base))


scenario['import_dep'] = scenario['import']

power_tech = ['chp_biofuel_extraction',
              'chp_hydrogen',
              'chp_methane_extraction',
              'chp_wte_back_pressure',
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

geo = geopandas.read_file('{}/portugal_regions.geojson'.format(base))

scenario = scenario.replace({np.nan: None})
project = Project.objects.create(name="PT 2050 - Decarbonisation",
                                 description="This project gathers information and preferences of SEEDS tool users to tailor the modelling of transition scenarios for the Portuguese energy system regarding decarbonisation targets proposed for the year 2050.",
                                 configuration="{}")

print('Starting loading CSV files into database')

for g in geo.itertuples():

    # print('inserting:',g.index,g.region_name)
    s = ScenarioLocation.objects.create(project=project,
                                        location=g.index, region_name=g.region_name)
print('    Location data stored')

def getLocation(location):
    l = ScenarioLocation.objects.filter(location=location)
    if len(l) == 0:
        s = ScenarioLocation.objects.create(project=project,
                                            location=location, region_name=location)
        return s
    else:
        return l[0]


scenario['id'] = scenario.index
scenario['id'] = scenario['id'].astype('int')
# Iterating through all data and populate Scenario table
for s in scenario.itertuples():
    try:
        """
        print(dict(project=project,
                   power_capacity=s.power,
                   storage_capacity=s.storage,
                   community_infrastructure=s.infra,
                   import_dependency=s.import_dep,
                   implementation_pace=s.pace,
                   bio_fuel=s.bio,
                   wind_onshore=s.wind_onshore if s.wind_onshore else None,
                   wind_offshore=s.wind_offshore if s.wind_offshore else None,
                   open_field_pv=s.open_field_pv if s.open_field_pv else None,
                   roof_mounted_pv=s.roof_mounted_pv if s.roof_mounted_pv else None,
                   hydro_run_of_river=s.hydro_run_of_river if s.hydro_run_of_river else None,
                   global_warming=s.global_warming,
                   land_occupation=s.land_occupation,
                   surplus_ore=s.surplus_ore,
                   water_consumption=s.water_consumption,
                   freshwater_eutrophication=s.freshwater_eutrophication,
                   battery=s.battery
                   ))
        """
        s_record = Scenario.objects.create(project=project, power_capacity=s.power,
                                           storage_capacity=s.storage,
                                           community_infrastructure=s.infra,
                                           import_dependency=s.import_dep,
                                           implementation_pace=s.pace,
                                           bio_fuel=s.bio,
                                           max_regional_share=s.max_regional_share,
                                           wind_onshore=s.wind_onshore,
                                           wind_offshore=s.wind_offshore,
                                           open_field_pv=s.open_field_pv,
                                           roof_mounted_pv=s.roof_mounted_pv,
                                           hydro_run_of_river=s.hydro_run_of_river,
                                           global_warming=s.global_warming,
                                           land_occupation=s.land_occupation,
                                           surplus_ore=s.surplus_ore,
                                           water_consumption=s.water_consumption,
                                           freshwater_eutrophication=s.freshwater_eutrophication,
                                           battery=s.battery,
                                           hydrogen=s.chp_hydrogen
                                           )

    except ValidationError as e:
        print(e)

        break
    tech_gen_s = tech_gen.loc[tech_gen['scenario'] == s.id, :]
    tech_sto_s = tech_sto.loc[tech_sto['scenario'] == s.id, :]

    for tech_gen_record in tech_gen_s.itertuples():
        tg = TechGeneration.objects.create(project=project, scenario=s_record,
                                           location=getLocation(
                                               tech_gen_record.location),
                                           technology_type=tech_gen_record.tech_type,
                                           energy_generation=tech_gen_record.value)
    for tech_sto_record in tech_sto_s.itertuples():
        ts = TechStorage.objects.create(project=project, scenario=s_record,
                                        location=getLocation(
                                            tech_sto_record.location),
                                        technology_type=tech_sto_record.tech_type,
                                        energy_storage=tech_sto_record.value)

    # Populating electrification tables
    ele_heat_s = ele_heat[ele_heat['spores'] == s.id]
    ele_road_s = ele_road[ele_road['spores'] == s.id]

    for ele_heat_record in ele_heat_s.itertuples():
        ehs = Electrification.objects.create(project=project, scenario=s_record,
                                             location=ele_heat_record.locs,
                                             carriers_type='heat',
                                             electrification_rate=ele_heat_record.electrification_rate_heat_building)

    for ele_road_record in ele_road_s.itertuples():
        ers = Electrification.objects.create(project=project, scenario=s_record,
                                             location=ele_road_record.locs,
                                             carriers_type='transport',
                                             electrification_rate=ele_road_record.electrification_rate_road_transport)


    # Populating energy supply table
    energy_tech_s = energy_tech[energy_tech['spores'] == s.id]
    for energy_tech_record in energy_tech_s.itertuples():
        esr = EnergySupply.objects.create(project=project, scenario=s_record,
                                          location=getLocation(
                                              energy_tech_record.locs),
                                          technology_type=energy_tech_record.techs,
                                          energy_supply=energy_tech_record.energy_supply)
    # Populating transmission table
    transmission_s = transmission[transmission['spores'] == s.id]
    for transmission_record in transmission_s.itertuples():
        tr = EnergyTransmission.objects.create(project=project, scenario=s_record,
                                               from_location=transmission_record.exporting_region,
                                               to_location=transmission_record.importing_region,
                                               transmission_capacity=transmission_record.transmission_capacity)
        
    # Populating GeneratedHeat table
    build_heat_s = build_heat[build_heat['spores'] == s.id]
    district_heat_s = district_heat[district_heat['spores'] == s.id]
    
    for build_heat_record  in build_heat_s.itertuples():
        bh = GeneratedHeat.objects.create(project=project, scenario=s_record,
                                          location = getLocation(
                                              build_heat_record.locs),
                                          technology_type=build_heat_record.techs,
                                          heat_type = 'building',
                                          heat = build_heat_record.generated_building_heat)
        
    for dis_heat_record  in district_heat_s.itertuples():
        bh = GeneratedHeat.objects.create(project=project, scenario=s_record,
                                          location = getLocation(
                                              dis_heat_record.locs),
                                          technology_type=dis_heat_record.techs,
                                          heat_type = 'district',
                                          heat = dis_heat_record.generated_district_heat)

        
    # Populating GeneratedTransport table 
    road_transport_s = road_transport[road_transport['spores'] == s.id]
    for road_transport_record  in road_transport_s.itertuples():
        gt = GeneratedTransport.objects.create(project=project, scenario=s_record,
                                          location = getLocation(
                                              road_transport_record.locs),
                                          technology_type=road_transport_record.techs,
                                          transport = road_transport_record.generated_road_transport)
        
    # Populating FlowOut table 
    flow_out_s = flow_out[flow_out['spores'] == s.id]
    for flow_out_record  in flow_out_s.itertuples():
        if np.isnan(flow_out_record.flow_out_sum):
            fo = FlowOut.objects.create(project=project, scenario=s_record,
                                          location = getLocation(
                                              flow_out_record.locs),
                                          technology_type=flow_out_record.techs,
                                          carriers = flow_out_record.carriers)
        else:
            fo = FlowOut.objects.create(project=project, scenario=s_record,
                                          location = getLocation(
                                              flow_out_record.locs),
                                          technology_type=flow_out_record.techs,
                                          carriers = flow_out_record.carriers,
                                          flow_out_sum = flow_out_record.flow_out_sum)
        
    print('  Scenario: {} data saved in database.'.format(s.id))

print('Completed !')
