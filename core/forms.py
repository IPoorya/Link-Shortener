from django import forms
from .models import *


class getURL(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['base_url']

class getCustomURL(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['base_url', 'short_url']

class getPassword(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['base_url', 'short_url', 'password']

    def clean_short_url(self):
        cleaned_data = super().clean()
        short_url = cleaned_data.get('short_url')
        data = short_url[short_url.rfind("/"):]
        return data

class checkPassword(forms.Form):
    password = forms.CharField(max_length=31)


class urlUsage(forms.Form):
    url = forms.CharField(label='URL:')


