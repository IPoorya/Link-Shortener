from django.urls import path, re_path
from .views import home, urlGenerator, customUrlGenerator, setPassword, shortUrl

urlpatterns = [
    path('', home.as_view(), name='home'),
    path('url-generator/', urlGenerator.as_view(), name='urlgenerator'),
    path('custom-url-generator/', customUrlGenerator.as_view(), name='customurlgenerator'),
    path('set-password/', setPassword.as_view(), name='setpassword'),
    re_path(r'^[a-zA-Z0-9]*$', shortUrl.as_view()),
]