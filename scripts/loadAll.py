from seeds_bootstrap.models import Scenario, ScenarioLocation, TechGeneration, TechStorage, ImpactGeneration, ImpactStorage
import pandas as pd
import geopandas
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

base = '/Users/htk/Documents/Work/Seeds_project/seeds_bootstrap copy/scripts'
# Data files for Scenario table

scenario = pd.read_csv('{}/Scenario.csv'.format(base))
impact_gen = pd.read_csv('{}/ImpactGeneration.csv'.format(base))
impact_sto = pd.read_csv('{}/ImpactStorage.csv'.format(base))
tech_gen = pd.read_csv('{}/TechGeneration.csv'.format(base))
tech_sto = pd.read_csv('{}/TechStorage.csv'.format(base))
scenario['import_dep'] = scenario['import']
geo = geopandas.read_file('{}/portugal_regions.geojson'.format(base))

for g in geo.itertuples():
    print('inserting:',g.index,g.region_name)
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

    s_record = Scenario.objects.create(power_capacity = s.power,
            storage_capacity = s.storage,
            community_infrastructure = s.infra,
            import_dependency = s.import_dep,
            implementation_pace = s.pace,
            bio_fuel = s.bio)
    print('------>')
    print(s_record)
    
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

    impact_gen_s = impact_gen.loc[tech_gen['scenario'] == s.id,:]
    impact_sto_s = impact_sto.loc[tech_sto['scenario'] == s.id,:]



    for impact_sto_record in impact_sto_s.itertuples():

        iss = ImpactStorage.objects.create(scenario=s_record,
                                           location=getLocation(impact_sto_record.location),
                                           technology_type=impact_sto_record.tech_type,
                                           land_occupation=impact_sto_record.land_occupation,
                                           marine_toxicity=impact_sto_record.marine_toxicity,
                                           human_toxicity=impact_sto_record.human_toxicity,
                                           metal_depletion=impact_sto_record.metal_depletion,
                                           fossil_depletion=impact_sto_record.fossil_depletion)



    print('------>Impact Sto done')
    for impact_gen_record in impact_gen_s.itertuples():
        ig = ImpactGeneration.objects.create(scenario=s_record,
                                             location=getLocation(impact_gen_record.location),
                                             technology_type=impact_gen_record.tech_type,
                                             land_occupation=impact_gen_record.land_occupation,
                                             marine_toxicity=impact_gen_record.marine_toxicity,
                                             human_toxicity=impact_gen_record.human_toxicity,
                                             metal_depletion=impact_gen_record.metal_depletion,
                                             fossil_depletion=impact_gen_record.fossil_depletion)

    print('------>Impact Gen done')


print('Data loading finished')
