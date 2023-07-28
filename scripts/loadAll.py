from seeds_bootstrap.models import Scenario, ScenarioLocation, TechGeneration, TechStorage, Impact
import pandas as pd
import geopandas
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
import numpy as np
base = '/Users/htk/Documents/Work/Seeds_project/seeds_bootstrap copy/scripts'
# Data files for Scenario table

scenario = pd.read_csv('{}/Scenario_extended.csv'.format(base))
impact = pd.read_csv('{}/Impact.csv'.format(base))
tech_gen = pd.read_csv('{}/TechGeneration.csv'.format(base))
tech_sto = pd.read_csv('{}/TechStorage.csv'.format(base))
scenario['import_dep'] = scenario['import']
geo = geopandas.read_file('{}/portugal_regions.geojson'.format(base))

scenario = scenario.replace({np.nan:None})

for g in geo.itertuples():
    #print('inserting:',g.index,g.region_name)
    s = ScenarioLocation.objects.create(location= g.index, region_name=g.region_name)

print('Location data stored')


def getLocation(location):
    l = ScenarioLocation.objects.filter(location=location)
    return l[0]

scenario['id'] = scenario.index
scenario['id'] = scenario['id'].astype('int')
# Iterating through all data and populate Scenario table
for s in scenario.itertuples():
    print('Scenario id:',int(s.id))
    try:
        print(dict(power_capacity = s.power,
            storage_capacity = s.storage,
            community_infrastructure = s.infra,
            import_dependency = s.import_dep,
            implementation_pace = s.pace,
            bio_fuel = s.bio,
            wind_onshore = s.wind_onshore if s.wind_onshore else None,
            wind_offshore = s.wind_offshore if s.wind_offshore else None,
            open_field_pv = s.open_field_pv if s.open_field_pv else None,
            roof_mounted_pv = s.roof_mounted_pv if s.roof_mounted_pv else None,
            hydro_run_of_river = s.hydro_run_of_river if s.hydro_run_of_river else None,
            climate_change = s.climate_change,
            land_occupation = s.land_occupation,
            fossil_depletion = s.fossil_depletion,
            marine_toxicity = s.marine_toxicity,
            human_toxicity = s.human_toxicity,
            metal_depletion = s.metal_depletion,
            battery = s.battery
            ))
        s_record = Scenario.objects.create(power_capacity = s.power,
            storage_capacity = s.storage,
            community_infrastructure = s.infra,
            import_dependency = s.import_dep,
            implementation_pace = s.pace,
            bio_fuel = s.bio,
            wind_onshore = s.wind_onshore,
            wind_offshore = s.wind_offshore,
            open_field_pv = s.open_field_pv,
            roof_mounted_pv = s.roof_mounted_pv,
            hydro_run_of_river = s.hydro_run_of_river,
            climate_change = s.climate_change,
            land_occupation = s.land_occupation,
            fossil_depletion = s.fossil_depletion,
            marine_toxicity = s.marine_toxicity,
            human_toxicity = s.human_toxicity,
            metal_depletion = s.metal_depletion,
            battery = s.battery
            )
        

    except ValidationError as e:
        print(e)
        
        break
    print('------>')

    
    tech_gen_s = tech_gen.loc[tech_gen['scenario'] == s.id,:]
    tech_sto_s = tech_sto.loc[tech_sto['scenario'] == s.id,:]

    for tech_gen_record in tech_gen_s.itertuples():
        tg = TechGeneration.objects.create(scenario=s_record,
                                           location=getLocation(tech_gen_record.location),
                                           technology_type=tech_gen_record.tech_type,
                                           energy_generation=tech_gen_record.value)

    print('------>Tech Gen done')
    for tech_sto_record in tech_sto_s.itertuples():
        ts = TechStorage.objects.create(scenario=s_record,
                                        location=getLocation(tech_sto_record.location),
                                        technology_type=tech_sto_record.tech_type,
                                        energy_storage=tech_sto_record.value)
    print('------>Tech Sto done')
    impact_s = impact.loc[tech_gen['scenario'] == s.id,:]

    for impact_s_record in impact_s.itertuples():

        iss = Impact.objects.create(scenario=s_record,
                                           location=getLocation(impact_s_record.location),
                                           technology_type=impact_s_record.tech_type,
                                           land_occupation=impact_s_record.land_occupation,
                                           marine_toxicity=impact_s_record.marine_toxicity,
                                           human_toxicity=impact_s_record.human_toxicity,
                                           metal_depletion=impact_s_record.metal_depletion,
                                           fossil_depletion=impact_s_record.fossil_depletion)



    print('------>Impact done')

print('Data loading finished')
