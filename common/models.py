from django.db import models


class BaseSpecies(models.Model):
    name = models.CharField(max_length=100, verbose_name='Espèce', unique=True)

    def __str__(self):
        return self.name


class BaseVariety(models.Model):
    name = models.CharField(max_length=100, verbose_name='Variétée', unique=True)
    species = models.ForeignKey(BaseSpecies, on_delete=models.CASCADE)


class BaseOperation(models.Model):
    class Meta:
        unique_together = ('name', 'variety')

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Opération')
    variety = models.ForeignKey(BaseVariety, on_delete=models.CASCADE)



