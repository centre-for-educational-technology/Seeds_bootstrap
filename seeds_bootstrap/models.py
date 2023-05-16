from django.db import models

class Scenario(models.Model):
    scenario_id              = models.IntegerField(primary_key=True)
    power_capacity           = models.DecimalField(max_digits = 7, decimal_places=2)
    storage_capacity         = models.DecimalField(max_digits = 7, decimal_places=2)
    community_infrastructure = models.DecimalField(max_digits = 7, decimal_places=2)
    implementation_pace      = models.DecimalField(max_digits = 7, decimal_places=2)
    import_dependecy         = models.DecimalField(max_digits = 7, decimal_places=2)


class ScenarioLocation(models.Model):
    """
    Model for storing each scenario location information
    """
    scenario_id = models.ForeignKey(Scenario,on_delete = models.CASCADE)
    location_id = models.CharField(max_length = 20)
    region_name = models.CharField(max_length = 20)

    class Meta:
        models.UniqueConstraint(fields=['scenario_id', 'location_id'], name='unique_location')


class TechGeneration(models.Model):
    """
    Model to store technology wise energy generation.
    """
    location_id = models.ForeignKey(ScenarioLocation,on_delete=models.CASCADE)
    technology_type = models.CharField(max_length = 20)
    energy_generation = models.DecimalField(max_digits = 7, decimal_places=2)

    class Meta:
        models.UniqueConstraint(fields=['location_id', 'technology_type'], name='unique_location_tech')



class TechStorage(models.Model):
    """
    Model to store technology wise storage capacity.
    """
    location_id = models.ForeignKey(ScenarioLocation,on_delete=models.CASCADE)
    technology_type = models.CharField(max_length = 20)
    energy_storage = models.DecimalField(max_digits = 7, decimal_places=2)

    class Meta:
        models.UniqueConstraint(fields=['location_id', 'technology_type'], name='unique_location_tech')



class ImpactGeneration(models.Model):
    """
    Model to store technology wise energy generation.
    """
    location_id = models.ForeignKey(ScenarioLocation,on_delete=models.CASCADE)
    technology_type = models.CharField(max_length = 20)
    land_occupation = models.DecimalField(max_digits = 7, decimal_places=2)
    marine_toxicity = models.DecimalField(max_digits = 7, decimal_places=2)
    human_toxicity  = models.DecimalField(max_digits = 7, decimal_places=2)
    fossil_depletion = models.DecimalField(max_digits = 7, decimal_places=2)
    metal_depletion  = models.DecimalField(max_digits = 7, decimal_places=2)

    class Meta:
        models.UniqueConstraint(fields=['location_id', 'technology_type'], name='unique_location_tech')



class ImpactStorage(models.Model):
    """
    Model to store technology wise energy generation.
    """
    location_id = models.ForeignKey(ScenarioLocation,on_delete=models.CASCADE)
    technology_type = models.CharField(max_length = 20)
    land_occupation = models.DecimalField(max_digits = 7, decimal_places=2)
    marine_toxicity = models.DecimalField(max_digits = 7, decimal_places=2)
    human_toxicity  = models.DecimalField(max_digits = 7, decimal_places=2)
    fossil_depletion = models.DecimalField(max_digits = 7, decimal_places=2)
    metal_depletion  = models.DecimalField(max_digits = 7, decimal_places=2)

    class Meta:
        models.UniqueConstraint(fields=['location_id', 'technology_type'], name='unique_location_tech')
