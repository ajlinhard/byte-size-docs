# Django Overview

Django is a high-level Python web framework designed for rapid development of secure and maintainable websites. It follows the "batteries-included" philosophy and the Model-View-Template (MVT) architectural pattern.

## Use Cases

Django is ideal for building complex, database-driven websites and web applications. It's particularly well-suited for:

- Content management systems
- Social media platforms
- E-commerce sites
- Enterprise applications
- RESTful APIs
- Real-time applications (with channels)
- Scientific or data-driven platforms

## Django Cheatsheet

### Project Setup

```python
# Install Django
pip install django

# Create a project
django-admin startproject myproject

# Create an app
python manage.py startapp myapp

# Run development server
python manage.py runserver

# Create database tables
python manage.py migrate

# Create migrations
python manage.py makemigrations
```

### Models (Database)

```python
# models.py - Basic model
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

# Common field types
models.CharField(max_length=100)
models.TextField()
models.IntegerField()
models.DecimalField(max_digits=10, decimal_places=2)
models.BooleanField(default=False)
models.DateTimeField(auto_now_add=True)  # Set when created
models.DateTimeField(auto_now=True)      # Updated each save
models.ForeignKey('AnotherModel', on_delete=models.CASCADE)
models.ManyToManyField('AnotherModel')
models.OneToOneField('AnotherModel', on_delete=models.CASCADE)
models.ImageField(upload_to='images/')
models.FileField(upload_to='files/')
models.JSONField()  # Django 3.1+
```

### Views

```python
# Function-based views
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'myapp/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'myapp/product_detail.html', {'product': product})

# Class-based views
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class ProductListView(ListView):
    model = Product
    template_name = 'myapp/product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'price', 'description']
    success_url = reverse_lazy('product-list')
```

### URLs

```python
# urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    # Function-based views
    path('products/', views.product_list, name='product-list'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),
    
    # Class-based views
    path('cbv/products/', views.ProductListView.as_view(), name='cbv-product-list'),
    path('cbv/products/create/', views.ProductCreateView.as_view(), name='cbv-product-create'),
    
    # Path converters
    path('products/<int:pk>/', views.product_detail),    # Integer
    path('products/<str:slug>/', views.product_detail),  # String
    path('products/<uuid:id>/', views.product_detail),   # UUID
    path('products/<slug:slug>/', views.product_detail), # Slug
    
    # Include other URL patterns
    path('api/', include('myapp.api.urls')),
]
```

### Templates

```html
<!-- Base template: base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <header>My Django Site</header>
    <main>
        {% block content %}
        {% endblock %}
    </main>
    <footer>© 2025</footer>
</body>
</html>

<!-- Child template: product_list.html -->
{% extends 'base.html' %}

{% block title %}Products{% endblock %}

{% block content %}
    <h1>Products</h1>
    <ul>
        {% for product in products %}
            <li>
                <a href="{% url 'product-detail' product.id %}">
                    {{ product.name }} - ${{ product.price }}
                </a>
            </li>
        {% empty %}
            <li>No products available.</li>
        {% endfor %}
    </ul>
{% endblock %}
```

### Forms

```python
# forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

# Custom form
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    
    def clean_email(self):
        """Custom validation"""
        email = self.cleaned_data['email']
        if not email.endswith('@example.com'):
            raise forms.ValidationError("Only example.com emails allowed")
        return email
```

### Authentication

```python
# Settings for authentication
# settings.py
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# URLs for authentication
# urls.py
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]

# Protect views with login_required
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

# For class-based views
from django.contrib.auth.mixins import LoginRequiredMixin

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
```

### Advanced Features

#### REST API with Django REST Framework

```python
# Install
pip install djangorestframework

# Add to INSTALLED_APPS
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
]

# serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description']

# views.py
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# urls.py
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

#### Custom Management Commands

```python
# myapp/management/commands/import_data.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Import data from a CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to CSV file')
        
    def handle(self, *args, **options):
        file_path = options['file_path']
        self.stdout.write(f'Importing data from {file_path}')
        # Import logic here
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))

# Run with: python manage.py import_data path/to/file.csv
```

#### Signals

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Register in apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'myapp'
    
    def ready(self):
        import myapp.signals
```

#### Middleware

```python
# middleware.py
class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Code executed before the view
        
        response = self.get_response(request)
        
        # Code executed after the view
        
        return response

# Add to settings.py
MIDDLEWARE = [
    # Django middleware
    'django.middleware.security.SecurityMiddleware',
    # ...
    # Custom middleware
    'myapp.middleware.SimpleMiddleware',
]
```

#### Caching

```python
# settings.py - Cache setup
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Cache a view
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def my_view(request):
    # ...
    return response

# Cache a template fragment
{% load cache %}
{% cache 500 sidebar %}
    {# sidebar content #}
{% endcache %}

# Low-level API
from django.core.cache import cache

# Store value
cache.set('my_key', 'my_value', timeout=300)  # 5 minutes

# Get value
value = cache.get('my_key')

# Delete value
cache.delete('my_key')
```

This cheatsheet covers the basics to more complex Django features. Django is a powerful framework with many more capabilities beyond what's listed here, including testing frameworks, admin customization, internationalization, and more advanced features like Django Channels for WebSockets.
