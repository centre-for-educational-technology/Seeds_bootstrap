from seeds_bootstrap.models import Scenario
from seeds_bootstrap.models import ScenarioLocation, TechGeneration
from seeds_bootstrap.models import TechStorage
from seeds_bootstrap.models import Electrification
from seeds_bootstrap.models import EnergySupply
from seeds_bootstrap.models import EnergyTransmission
from seeds_bootstrap.models import Project

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


transmission = pd.read_csv('{}/energy/transmission_capacity.csv'.format(base))
energy_tech = pd.read_csv('{}/energy/energy_supply.csv'.format(base))


ele_heat = pd.read_csv(
    '{}/energy/electrification_rate_heat_building.csv'.format(base))
ele_road = pd.read_csv(
    '{}/energy/electrification_rate_road_transport.csv'.format(base))

geo = geopandas.read_file('{}/portugal_regions.geojson'.format(base))

scenario = scenario.replace({np.nan: None})
project = Project.objects.create(name="PT 2050 - Decarbonisation",
                                 description="This project gathers information and preferences of SEEDS tool users to tailor the modelling of transition scenarios for the Portuguese energy system regarding decarbonisation targets proposed for the year 2050.",
                                 configuration="{}")

for g in geo.itertuples():
    continue
    # print('inserting:',g.index,g.region_name)
    s = ScenarioLocation.objects.create(project=project,
                                        location=g.index, region_name=g.region_name)

print('Location data stored')


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
    print('Scenario id:', int(s.id))
    try:
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
        s_record = Scenario.objects.create(project=project, power_capacity=s.power,
                                           storage_capacity=s.storage,
                                           community_infrastructure=s.infra,
                                           import_dependency=s.import_dep,
                                           implementation_pace=s.pace,
                                           bio_fuel=s.bio,
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
                                           battery=s.battery
                                           )

    except ValidationError as e:
        print(e)

        break
    print('------>')

    tech_gen_s = tech_gen.loc[tech_gen['scenario'] == s.id, :]
    tech_sto_s = tech_sto.loc[tech_sto['scenario'] == s.id, :]

    for tech_gen_record in tech_gen_s.itertuples():
        tg = TechGeneration.objects.create(project=project, scenario=s_record,
                                           location=getLocation(
                                               tech_gen_record.location),
                                           technology_type=tech_gen_record.tech_type,
                                           energy_generation=tech_gen_record.value)

    print('------>Tech Gen done')
    for tech_sto_record in tech_sto_s.itertuples():
        ts = TechStorage.objects.create(project=project, scenario=s_record,
                                        location=getLocation(
                                            tech_sto_record.location),
                                        technology_type=tech_sto_record.tech_type,
                                        energy_storage=tech_sto_record.value)
    print('------>Tech Sto done')
    impact_s = impact.loc[tech_gen['scenario'] == s.id, :]

    """
    # 
    for impact_s_record in impact_s.itertuples():

        iss = Impact.objects.create(project=project, scenario=s_record,
                                    location=getLocation(
                                        impact_s_record.location),
                                    technology_type=impact_s_record.tech_type,
                                    land_occupation=impact_s_record.land_occupation,
                                    marine_toxicity=impact_s_record.marine_toxicity,
                                    human_toxicity=impact_s_record.human_toxicity,
                                    metal_depletion=impact_s_record.metal_depletion,
                                    fossil_depletion=impact_s_record.fossil_depletion)

    print('------>Impact done')
    """

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

    print('------>Electrification done')

    """
        print({'scenario':s.id,
              'location':ele_road_s.locs,
              'carriers_type':'transport',
              'electrification_rate':ele_road_s.electrification_rate_road_transport})
        """

    # Populating energy supply table
    energy_tech_s = energy_tech[energy_tech['spores'] == s.id]
    for energy_tech_record in energy_tech_s.itertuples():
        esr = EnergySupply.objects.create(project=project, scenario=s_record,
                                          location=getLocation(
                                              energy_tech_record.locs),
                                          technology_type=energy_tech_record.techs,
                                          energy_supply=energy_tech_record.energy_supply)
    print('------>Energy supply done')

    # Populating transmission table
    transmission_s = transmission[transmission['spores'] == s.id]
    for transmission_record in transmission_s.itertuples():
        tr = EnergyTransmission.objects.create(project=project, scenario=s_record,
                                               from_location=transmission_record.exporting_region,
                                               to_location=transmission_record.importing_region,
                                               transmission_capacity=transmission_record.transmission_capacity)
    print('------>Transmission done')

print('Data loading finished')
