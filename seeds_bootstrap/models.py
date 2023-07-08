from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
import datetime


class Scenario(models.Model):
    """
    Model for storing each scenario information
    """
    power_capacity = models.DecimalField(max_digits=25, decimal_places=10)
    storage_capacity = models.DecimalField(max_digits=25, decimal_places=10)
    community_infrastructure = models.DecimalField(
        max_digits=25, decimal_places=10)
    implementation_pace = models.DecimalField(max_digits=25, decimal_places=10)
    import_dependency = models.DecimalField(max_digits=25, decimal_places=10)
    bio_fuel = models.DecimalField(max_digits=25, decimal_places=10, default=0)


class ScenarioLocation(models.Model):
    """
    Model for storing each scenario location information
    """
    location = models.CharField(max_length=20)
    region_name = models.CharField(max_length=20)


class TechGeneration(models.Model):
    """
    Model to store technology wise energy generation and storage.
    """
    location = models.ForeignKey(ScenarioLocation, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    technology_type = models.CharField(max_length=20)
    energy_generation = models.DecimalField(max_digits=25, decimal_places=10)

    class Meta:
        models.UniqueConstraint(fields=[
                                'location_id', 'scenario_id', 'technology_type'], name='unique_location_tech')


class TechStorage(models.Model):
    """
    Model to store technology wise energy storage.
    """
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    location = models.ForeignKey(ScenarioLocation, on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    technology_type = models.CharField(max_length=20)
    energy_storage = models.DecimalField(max_digits=25, decimal_places=10)

    class Meta:
        models.UniqueConstraint(fields=[
                                'location_id', 'scenario_id', 'technology_type'], name='unique_location_tech')


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
    infra_min = models.DecimalField(max_digits=25, decimal_places=10)
    infra_max = models.DecimalField(max_digits=25, decimal_places=10)
    pace_min = models.DecimalField(max_digits=25, decimal_places=10)
    pace_max = models.DecimalField(max_digits=25, decimal_places=10)
    import_min = models.DecimalField(max_digits=25, decimal_places=10)
    import_max = models.DecimalField(max_digits=25, decimal_places=10)
    erate_build_min = models.DecimalField(max_digits=25, decimal_places=10)
    erate_build_max = models.DecimalField(max_digits=25, decimal_places=10)
    erate_transport_min = models.DecimalField(max_digits=25, decimal_places=10)
    erate_transport_max = models.DecimalField(max_digits=25, decimal_places=10)

    # Impact controls parameters
    marine_min = models.DecimalField(max_digits=25, decimal_places=10)
    marine_max = models.DecimalField(max_digits=25, decimal_places=10)
    agri_min = models.DecimalField(max_digits=25, decimal_places=10)
    agri_max = models.DecimalField(max_digits=25, decimal_places=10)
    human_min = models.DecimalField(max_digits=25, decimal_places=10)
    human_max = models.DecimalField(max_digits=25, decimal_places=10)
    climate_min = models.DecimalField(max_digits=25, decimal_places=10)
    climate_max = models.DecimalField(max_digits=25, decimal_places=10)
    fossil_min = models.DecimalField(max_digits=25, decimal_places=10)
    fossil_max = models.DecimalField(max_digits=25, decimal_places=10)
    metal_min = models.DecimalField(max_digits=25, decimal_places=10)
    metal_max = models.DecimalField(max_digits=25, decimal_places=10)

    # Energy technologies parameters
    roof_pv_min = models.DecimalField(max_digits=25, decimal_places=10)
    roof_pv_max = models.DecimalField(max_digits=25, decimal_places=10)
    open_pv_min = models.DecimalField(max_digits=25, decimal_places=10)
    open_pv_max = models.DecimalField(max_digits=25, decimal_places=10)
    hydro_river_min = models.DecimalField(max_digits=25, decimal_places=10)
    hydro_river_max = models.DecimalField(max_digits=25, decimal_places=10)
    hydro_pumped_min = models.DecimalField(max_digits=25, decimal_places=10)
    hydro_pumped_max = models.DecimalField(max_digits=25, decimal_places=10)
    hydro_reservoir_min = models.DecimalField(max_digits=25, decimal_places=10)
    hydro_reservoir_max = models.DecimalField(max_digits=25, decimal_places=10)
    hydrogen_min = models.DecimalField(max_digits=25, decimal_places=10)
    hydrogen_max = models.DecimalField(max_digits=25, decimal_places=10)
    wind_onshore_min = models.DecimalField(max_digits=25, decimal_places=10)
    wind_onshore_max = models.DecimalField(max_digits=25, decimal_places=10)
    wind_offshore_min = models.DecimalField(max_digits=25, decimal_places=10)
    wind_offshore_max = models.DecimalField(max_digits=25, decimal_places=10)
    trans_min = models.DecimalField(max_digits=25, decimal_places=10)
    trans_max = models.DecimalField(max_digits=25, decimal_places=10)
    battery_min = models.DecimalField(max_digits=25, decimal_places=10)
    battery_max = models.DecimalField(max_digits=25, decimal_places=10)


admin.site.register(Scenario)
admin.site.register(ScenarioLocation)
admin.site.register(TechGeneration)
admin.site.register(TechStorage)
admin.site.register(ImpactGeneration)
admin.site.register(ImpactStorage)

# Function to check if item is in the list
