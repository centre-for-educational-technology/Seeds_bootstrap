from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # other fields here

    sector = models.CharField(max_length=100)
    role = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    region_of_interest = models.CharField(max_length=200)
    other_regions = models.CharField(max_length=200, blank=True)
    aspects_socio = models.BooleanField(default=False)
    aspects_environment = models.BooleanField(default=False)
    aspects_technology = models.BooleanField(default=False)
    aspects_political = models.BooleanField(default=False)
    aspects_industry = models.BooleanField(default=False)
    aspects_oprationalisation = models.BooleanField(default=False)

    topics_energy_suppy = models.BooleanField(default=False)
    topics_impact = models.BooleanField(default=False)
    topics_my_region = models.BooleanField(default=False)
    topics_innovation = models.BooleanField(default=False)

    use_learn = models.BooleanField(default=False)
    use_advocacy = models.BooleanField(default=False)
    use_research = models.BooleanField(default=False)
    use_reports = models.BooleanField(default=False)
    use_education = models.BooleanField(default=False)
    use_investment = models.BooleanField(default=False)
    use_policy = models.BooleanField(default=False)
    use_planning = models.BooleanField(default=False)
    use_other = models.BooleanField(default=False)
    use_not_sure = models.BooleanField(default=False)
