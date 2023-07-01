from seeds_bootstrap.models import Scenario, ScenarioLocation, TechCapacity
import pandas as pd

base= '/Users/htk/Documents/Work/Seeds_project/seeds_bootstrap/scripts'
# Data files for Scenario table
nameplate = pd.read_csv('{}/energy/nameplate_capacity.csv'.format(base))
storage = pd.read_csv('{}/energy/storage_capacity.csv'.format(base))
citizen = pd.read_csv('{}/energy/citizen_leadership_degree.csv'.format(base))
acc = pd.read_csv('{}/energy/deployment_acceleration_rate.csv'.format(base))
imp = pd.read_csv('{}/energy/import_dependency.csv'.format(base))
bio = pd.read_csv('{}/energy/biofuel_use_rate.csv'.format(base))

power_tech = ['pumped_hydro', 
              'hydro_reservoir', 
              'hydro_run_of_river', 
              'open_field_pv', 
              'roof_mounted_pv', 
              'wind_offshore', 
              'wind_onshore_competing', 
              'wind_onshore_monopoly', 
              'existing_wind', 
              'existing_pv', 
              'ccgt', 
              'chp_biofuel_extraction',
              'chp_hydrogen',
              'chp_methane_extraction',
              'chp_wte_back_pressure']

# Preparing dataset for main Scenario table

# Computing total power capacity of scenario
pw_nameplate = nameplate.loc[nameplate['techs'].isin(power_tech),:]
total_power = pw_nameplate.groupby(['spores']).sum().reset_index()

# Computing total storage capacity scenario wise
pw_storage = storage.loc[storage['techs'].isin(power_tech),:]
total_storage = storage.groupby(['spores']).sum().reset_index()

print(' Files opened successfully')
# Iterating through all data and populate Scenario table
for spore in acc.spores.unique():
    scenario_id = spore
    infrastructure = citizen.loc[citizen['spores'] == spore,'citizen_leadership_degree'].to_list()[0]
    deployment_rate = acc.loc[acc['spores'] == spore,'deployment_acceleration_rate'].to_list()[0]
    import_dependency = imp.loc[imp['spores'] == spore,'import_dependency'].to_list()[0]
    power_capacity = total_power.loc[total_power['spores'] == spore,'nameplate_capacity'].to_list()[0]
    storage_capacity = total_storage.loc[total_storage['spores'] == spore,'storage_capacity'].to_list()[0]
    bio_fuel = bio.loc[bio['spores'] == spore,'biofuel_use_rate'].to_list()[0]
    
    s = Scenario.objects.create(power_capacity = power_capacity,
                        storage_capacity = storage_capacity,
                        import_dependecy = import_dependency,
                        community_infrastructure = infrastructure,
                        implementation_pace = deployment_rate,
                        bio_fuel = bio_fuel)
    
    print('Added object')
    
    """
    print('Object:')
    print('   infrastructure:',infrastructure)
    print('   deployment_rate:',deployment_rate)
    print('   import_dependency:',import_dependency)
    print('   power_capacity:',power_capacity)
    print('   storage_capacity:',storage_capacity)
    print('   biofule_use_rate:',bio_fuel)

    """