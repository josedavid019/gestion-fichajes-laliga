from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    flag_url = models.URLField(blank=True)

    class Meta:
        db_table = "players_country"

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=20, default="league")

    class Meta:
        db_table = "players_competition"

    def __str__(self):
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=20, unique=True)
    year_start = models.PositiveSmallIntegerField()
    year_end = models.PositiveSmallIntegerField()
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = "players_season"

    def __str__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=100, blank=True)
    logo_url = models.URLField(blank=True)

    class Meta:
        db_table = "players_club"

    def __str__(self):
        return self.name


class Player(models.Model):
    STATUS = [
        ("active", "Activo"),
        ("injured", "Lesionado"),
        ("suspended", "Sancionado"),
        ("retired", "Retirado"),
        ("free_agent", "Libre"),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    alias = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    current_club = models.ForeignKey(
        Club, on_delete=models.SET_NULL, null=True, blank=True
    )
    position = models.CharField(max_length=20, blank=True)
    shirt_number = models.PositiveSmallIntegerField(null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.PositiveSmallIntegerField(null=True, blank=True)
    preferred_foot = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    market_value_eur = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    photo_url = models.URLField(blank=True)
    face_embedding = models.JSONField(null=True, blank=True)
    external_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players_player"

    def __str__(self):
        return self.alias or f"{self.first_name} {self.last_name}"
