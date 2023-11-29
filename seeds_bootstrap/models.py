from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
import datetime


class Project(models.Model):
    """
    Model for storing project details
    """
    name = models.TextField()
    description = models.TextField(blank=True)
    configuration = models.JSONField(blank=True)


class Scenario(models.Model):
    """
    Model for storing each scenario information
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    power_capacity = models.DecimalField(max_digits=25, decimal_places=10)
    storage_capacity = models.DecimalField(max_digits=25, decimal_places=10)
    community_infrastructure = models.DecimalField(
        max_digits=25, decimal_places=10)
    implementation_pace = models.DecimalField(max_digits=25, decimal_places=10)
    import_dependency = models.DecimalField(max_digits=25, decimal_places=10)
    bio_fuel = models.DecimalField(
        max_digits=25, decimal_places=10, blank=True)
    battery = models.DecimalField(max_digits=25, decimal_places=10, blank=True)

    # storing total energy generated for query params technology types
    roof_mounted_pv = models.DecimalField(
        max_digits=25, decimal_places=10, null=True)
    open_field_pv = models.DecimalField(
        max_digits=25, decimal_places=10, null=True)
    wind_onshore = models.DecimalField(
        max_digits=25, decimal_places=10, null=True)
    wind_offshore = models.DecimalField(
        max_digits=25, decimal_places=10, null=True)
    hydro_run_of_river = models.DecimalField(
        max_digits=25, decimal_places=10, null=True)
    hydrogen = models.DecimalField(
        max_digits=25, decimal_places=10, null=True)

    # storing total impact of scenario for electricity generation and storage
    land_occupation = models.DecimalField(max_digits=25, decimal_places=10)
    surplus_ore = models.DecimalField(max_digits=25, decimal_places=10)
    global_warming = models.DecimalField(max_digits=25, decimal_places=10)
    water_consumption = models.DecimalField(max_digits=25, decimal_places=10)
    freshwater_eutrophication = models.DecimalField(
        max_digits=25, decimal_places=10)


class Vote(models.Model):
    """
    Model for storing voted response
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    submitted_user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub_date = models.DateField(default=datetime.date.today)
    response = models.BooleanField(blank=True)


class UserScenario(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    submitted_user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modified = models.DateField(default=datetime.date.today)
    label = models.TextField(blank=True)


class ScenarioLocation(models.Model):
    """
    Model for storing each scenario location information
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    location = models.CharField(max_length=20)
    region_name = models.CharField(max_length=20)


class Electrification(models.Model):
    """
    Model to store electrification data.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    location = models.CharField(max_length=10)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    carriers_type = models.CharField(max_length=20)
    electrification_rate = models.DecimalField(
        max_digits=25, decimal_places=10)

    class Meta:
        models.UniqueConstraint(fields=[
                                'location_id',
                                'scenario_id',
                                'carriers_type'],
                                name='unique_location_carrier')


class EnergySupply(models.Model):
    """
    Model to store energy supply.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    location = models.ForeignKey(ScenarioLocation, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    technology_type = models.CharField(max_length=20)
    energy_supply = models.DecimalField(max_digits=25, decimal_places=10)

    class Meta:
        models.UniqueConstraint(fields=[
                                'project_id',
                                'location_id',
                                'scenario_id',
                                'technology_type'],
                                name='unique_location_tech')


class EnergyTransmission(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    from_location = models.CharField(max_length=10)
    to_location = models.CharField(max_length=10)
    transmission_capacity = models.DecimalField(
        max_digits=25, decimal_places=10)

    class Meta:
        models.UniqueConstraint(fields=[
                                'project_id',
                                'from_location_id',
                                'scenario_id',
                                'to_location_id'],
                                name='unique_from_to')


class TechGeneration(models.Model):
    """
    Model to store technology wise energy generation and storage.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    location = models.ForeignKey(ScenarioLocation, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    technology_type = models.CharField(max_length=20)
    energy_generation = models.DecimalField(max_digits=25, decimal_places=10)

    class Meta:
        models.UniqueConstraint(fields=[
                                'project_id',
                                'location_id',
                                'scenario_id',
                                'technology_type'],
                                name='unique_location_tech')


class TechStorage(models.Model):
    """
    Model to store technology wise energy storage.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    location = models.ForeignKey(ScenarioLocation, on_delete=models.CASCADE)
    technology_type = models.CharField(max_length=20)
    energy_storage = models.DecimalField(max_digits=25, decimal_places=10)

    class Meta:
        models.UniqueConstraint(fields=[
                                'project_id',
                                'location_id',
                                'scenario_id',
                                'technology_type'], name='unique_location_tech')


class ActivityLog(models.Model):
    """
    Model to store activity logs.
    Verbs:
        signed-in : user signed in the seeds platform
        submitted : user submitted the search query for filtering scenarios
        saved     : user saved scenario or search parameters
        compared  : user compared two scenarios
        downloaded: user downloaded the result of search parameters
        inspected : user inspected a scenario
        voted     : user voted a scenario
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    actor = models.EmailField(max_length=254)
    sub_date = models.DateTimeField(auto_now_add=True)
    verb = models.CharField(max_length=20)
    object = models.CharField(max_length=20)
    notes = models.CharField(max_length=200)


"""
class Impact(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    # location = models.ForeignKey(ScenarioLocation, on_delete=models.CASCADE)
    # technology_type = models.CharField(max_length=20)
    land_occupation = models.DecimalField(max_digits=25, decimal_places=10)
    surplus_ore = models.DecimalField(max_digits=25, decimal_places=10)
    global_warming = models.DecimalField(max_digits=25, decimal_places=10)
    water_consumption = models.DecimalField(max_digits=25, decimal_places=10)
    freshwater_eutrophication = models.DecimalField(
        max_digits=25, decimal_places=10)

    class Meta:

        models.UniqueConstraint(
            fields=[
                'project_id',
                'scenario_id',
                'location_id'], name='unique_location')



class ImpactGeneration(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    location = models.ForeignKey(ScenarioLocation, on_delete=models.CASCADE)
    technology_type = models.CharField(max_length=20)
    land_occupation = models.DecimalField(max_digits=25, decimal_places=10)
    marine_toxicity = models.DecimalField(max_digits=25, decimal_places=10)
    human_toxicity = models.DecimalField(max_digits=25, decimal_places=10)
    fossil_depletion = models.DecimalField(max_digits=25, decimal_places=10)
    metal_depletion = models.DecimalField(max_digits=25, decimal_places=10)

    class Meta:

        models.UniqueConstraint(
            fields=['location_id', 'technology_type'], name='unique_location_tech')


class ImpactStorage(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    location = models.ForeignKey(ScenarioLocation, on_delete=models.CASCADE)
    technology_type = models.CharField(max_length=20)
    land_occupation = models.DecimalField(max_digits=25, decimal_places=10)
    marine_toxicity = models.DecimalField(max_digits=25, decimal_places=10)
    human_toxicity = models.DecimalField(max_digits=25, decimal_places=10)
    fossil_depletion = models.DecimalField(max_digits=25, decimal_places=10)
    metal_depletion = models.DecimalField(max_digits=25, decimal_places=10)

    class Meta:
        models.UniqueConstraint(
            fields=['location_id', 'technology_type'], name='unique_location_tech')

"""


class QueryParameters(models.Model):
    """
    Model to store query parameters for future use
    """
    submitted_user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub_date = models.DateField(default=datetime.date.today)
    label = models.TextField(blank=True)

    # Energy systems parameters
    power_min = models.DecimalField(max_digits=25, decimal_places=10)
    power_max = models.DecimalField(max_digits=25, decimal_places=10)
    storage_min = models.DecimalField(max_digits=25, decimal_places=10)
    storage_max = models.DecimalField(max_digits=25, decimal_places=10)
    community_min = models.DecimalField(max_digits=25, decimal_places=10)
    community_max = models.DecimalField(max_digits=25, decimal_places=10)
    implementation_min = models.DecimalField(max_digits=25, decimal_places=10)
    implementation_max = models.DecimalField(max_digits=25, decimal_places=10)
    import_min = models.DecimalField(max_digits=25, decimal_places=10)
    import_max = models.DecimalField(max_digits=25, decimal_places=10)
    ele_heat_min = models.DecimalField(max_digits=25, decimal_places=10)
    ele_heat_max = models.DecimalField(max_digits=25, decimal_places=10)

    # Impact controls parameters
    global_min = models.DecimalField(max_digits=25, decimal_places=10)
    global_max = models.DecimalField(max_digits=25, decimal_places=10)
    land_min = models.DecimalField(max_digits=25, decimal_places=10)
    land_max = models.DecimalField(max_digits=25, decimal_places=10)
    water_min = models.DecimalField(max_digits=25, decimal_places=10)
    water_max = models.DecimalField(max_digits=25, decimal_places=10)
    fresh_min = models.DecimalField(max_digits=25, decimal_places=10)
    fresh_max = models.DecimalField(max_digits=25, decimal_places=10)
    surplus_min = models.DecimalField(max_digits=25, decimal_places=10)
    surplus_max = models.DecimalField(max_digits=25, decimal_places=10)

    # Energy technologies parameters
    photo_roof_min = models.DecimalField(max_digits=25, decimal_places=10)
    photo_roof_max = models.DecimalField(max_digits=25, decimal_places=10)
    photo_open_field_min = models.DecimalField(
        max_digits=25, decimal_places=10)
    photo_open_field_max = models.DecimalField(
        max_digits=25, decimal_places=10)
    # hydro_river_min = models.DecimalField(max_digits=25, decimal_places=10)
    # hydro_river_max = models.DecimalField(max_digits=25, decimal_places=10)
    # hydro_pumped_min = models.DecimalField(max_digits=25, decimal_places=10)
    # hydro_pumped_max = models.DecimalField(max_digits=25, decimal_places=10)
    # hydro_reservoir_min = models.DecimalField(max_digits=25, decimal_places=10)
    # hydro_reservoir_max = models.DecimalField(max_digits=25, decimal_places=10)
    hydrogen_min = models.DecimalField(max_digits=25, decimal_places=10)
    hydrogen_max = models.DecimalField(max_digits=25, decimal_places=10)
    wind_onshore_min = models.DecimalField(max_digits=25, decimal_places=10)
    wind_onshore_max = models.DecimalField(max_digits=25, decimal_places=10)
    wind_offshore_min = models.DecimalField(max_digits=25, decimal_places=10)
    wind_offshore_max = models.DecimalField(max_digits=25, decimal_places=10)
    transmission_min = models.DecimalField(max_digits=25, decimal_places=10)
    transmission_max = models.DecimalField(max_digits=25, decimal_places=10)
    bio_min = models.DecimalField(max_digits=25, decimal_places=10)
    bio_max = models.DecimalField(max_digits=25, decimal_places=10)
    battery_min = models.DecimalField(max_digits=25, decimal_places=10)
    battery_max = models.DecimalField(max_digits=25, decimal_places=10)


admin.site.register(Scenario)
admin.site.register(ScenarioLocation)
admin.site.register(TechGeneration)
admin.site.register(TechStorage)
admin.site.register(EnergySupply)
admin.site.register(EnergyTransmission)
admin.site.register(Electrification)
admin.site.register(Project)
admin.site.register(UserScenario)
admin.site.register(Vote)
admin.site.register(QueryParameters)
admin.site.register(ActivityLog)

# Function to check if item is in the list
