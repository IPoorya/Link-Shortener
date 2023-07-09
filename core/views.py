from django.shortcuts import render
from django.views import View
from .models import *
from .forms import *
import random
from django.utils.text import slugify
import string
from django.shortcuts import redirect
from datetime import datetime, timedelta
from django.db.models import Q
from django.db.models import Count
from django.http import HttpResponse

def generate_random_string(len):
    all_characters = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(string.digits)
    random_string = ''.join(random.choice(all_characters) for _ in range(len))
    return slugify(random_string)


class home(View):
    def get(self, request):
        return render(request, 'home.html', {
            'title' : 'Home'
        })
    

class urlGenerator(View):
    def get(self, request):
        form = getURL()
        return render(request, 'geturl.html', {
            'title' : 'URL Generator', 
            'form' : form,
            'generated' : 'false',
        })
    
    def post(self, request):
        form = getURL(request.POST)
        if not form.is_valid():
            return render(request, 'geturl.html', {
                'title' : 'URL Generator', 
                'form' : form,
                'generated' : 'false',
            })
        short_url = generate_random_string(5)
        while len(Link.objects.filter(short_url=short_url)) != 0:
            short_url = generate_random_string(5)
        Link.objects.create(base_url=request.POST.get('base_url'), short_url='/'+short_url)

    
        return render(request, 'geturl.html', {
            'title' : 'URL Generator', 
            'form' : form,
            'short_url' : f'{"https" if request.is_secure() else "http"}://{request.get_host()}/' + short_url,
            'generated' : 'true',
        })


class customUrlGenerator(View):
    def get(self, request):
        form = getCustomURL()
        return render(request, 'geturl.html', {
            'title' : 'Custom URL Generator', 
            'form' : form,
            'generated' : 'false',
        })
    
    def post(self, request):
        short_url = f'/{request.POST.get("short_url")}'
        form = getCustomURL(request.POST)
        if not form.is_valid():
            return render(request, 'geturl.html', {
                    'title' : 'Custom URL Generator', 
                    'form' : form,
                    'generated' : 'false',
                    'message' : 'invalid data!',
                })
        
        if len(Link.objects.filter(short_url=short_url)) == 1:
            return render(request, 'geturl.html', {
                    'title' : 'Custom URL Generator', 
                    'form' : form,
                    'generated' : 'false',
                    'message' : 'custom url already exists! pick another one'
                })
        
        else:
            short_url = f'/{request.POST.get("short_url")}'
            Link.objects.create(base_url=request.POST.get('base_url'), short_url=short_url)
            short_url = f'{"https" if request.is_secure() else "http"}://{request.get_host()}' + short_url

            return render(request, 'geturl.html', {
                'title' : 'Custom URL Generator', 
                'form' : form,
                'short_url' : short_url,
                'generated' : 'true',
            })


class setPassword(View):
    def get(self, request):
        form = getPassword()
        base_url = request.GET.get('base_url')
        short_url = request.GET.get('short_url')
        return render(request, 'setpassword.html', {
            'title' : 'Set Password', 
            'form' : form,
            'base_url' : base_url,
            'short_url' : short_url,
        })
    
    def post(self, request):
        base_url = request.POST.get('base_url')
        short_url = request.POST.get('short_url')[request.POST.get('short_url').rfind("/"):]
        password = request.POST.get('password')
        print('password: ', password)
        obj = Link.objects.get(base_url=base_url, short_url=short_url)
        print(obj)
        form = getPassword(request.POST, instance=obj)
        if not form.is_valid():
            return render(request, 'setpassword.html', {
            'title' : 'Set Password', 
            'form' : form,
            'short_url' : short_url,
            'message' : 'invalid data!',
            })
        form.save()       
        return render(request, 'setpassword.html', {
            'title' : 'Set Password', 
            'form' : form,
            'short_url' : request.POST.get('short_url'),
            'base_url' : base_url,
            'password' : password,
            'message' : 'success!',
            })
    

class shortUrl(View):
    def get(self, request):
        short_url = str(request.path)
        obj = Link.objects.filter(short_url=short_url)
        print(obj)
        if len(obj) == 1:
            obj = obj[0]
            if obj.password and len(obj.password) > 0:
                form = checkPassword()
                return render(request, 'getpassword.html', {
                    'title' : 'Check Password',
                    'form' : form, 
                })
            else:
                obj.usage_count += 1
                obj.save()
                usageChart.objects.create(url=obj)
                url = f'https://{obj.base_url}'
                return redirect(url)
            
        else:
            return render(request, '404.html', {
                'title' : '404',
                'message' : '404 page not found bro',
            })
        
    def post(self, request):
        form = checkPassword(request.POST)
        if not form.is_valid():
            return render(request, 'getpassword.html', {
                'form' : form,
                'message' : 'invalid data!',
            })
        short_url = str(request.path)
        password = request.POST.get('password')
        obj = Link.objects.filter(short_url=short_url).filter(password=password)
        if len(obj) == 1:
            obj = obj[0]
            url = f'https://{obj.base_url}'
            obj.usage_count += 1
            obj.save()
            usageChart.objects.create(url=obj)
            return redirect(url)
        return render(request, 'getpassword.html', {
            'form' : form,
            'message' : 'wrong password bro!',
        })


class stats(View):
    def get(self, request):
        form = urlUsage()
        return render(request, 'stats.html', {
            'form' : form,
            'title' : 'Stats',
            'method' : request.method,
        })

    def post(self, request):
        form = urlUsage(request.POST)
        if not form.is_valid():
            return render(request, 'stats.html', {
            'form' : form,
            'title' : 'Stats',
            'method' : request.method,
            'message' : 'invalid data!',
            }) 
        
        obj = Link.objects.get(short_url=form.cleaned_data['url'][form.cleaned_data['url'].rfind("/"):])
        data = []
        tempLable = [(datetime.now().date() - timedelta(days=30)).strftime('%m/%d')]
        label = []
        for i in range(30, 2, -3):
            start = datetime.now().date() - timedelta(days=i)
            end = datetime.now().date() - timedelta(days=i - 3)
            condition = Q(url=obj) & Q(usage_date__gte=start) & Q(usage_date__lte=end)
            data.append(len(usageChart.objects.filter(condition)))
            tempLable.append(end.strftime('%m/%d'))

        for i in range(len(tempLable)):
            if i != 10:
                label.append(tempLable[i] + '-' + tempLable[i + 1])

        total_usage = obj.usage_count
        last_usage = obj.last_usage
        return render(request, 'stats.html', {
            'title' : 'Stats',
            'form' : form,
            'chartData' : {
                'label': label,
                'data': data,
            },
            'total_usage' : total_usage,
            'last_usage' : last_usage,
        })