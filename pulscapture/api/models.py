from django.db import models


# Create your models here.
class PulseOutput(models.Model):
    def __str__(self):
        return self.name

    channel = models.IntegerField("Channel")
    name = models.CharField(max_length=200)


class Pulse(models.Model):
    pulse_output = models.ForeignKey(PulseOutput, on_delete=models.RESTRICT)
    created = models.DateTimeField(auto_now_add=True)
