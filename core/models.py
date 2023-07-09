from django.db import models

class Link(models.Model):
    base_url = models.CharField(max_length=1027)
    short_url = models.CharField(max_length=255, unique=True)
    last_usage = models.DateTimeField(auto_now=True)
    usage_count = models.PositiveBigIntegerField(default=0)
    password = models.CharField(max_length=31, null=True, blank=True)

    def __str__(self):
        return self.base_url + ':' + self.short_url


class usageChart(models.Model):
    url = models.ForeignKey(Link, on_delete=models.CASCADE, unique=False)
    usage_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url.base_url + ':' + self.url.short_url
