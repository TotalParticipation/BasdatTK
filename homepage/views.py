# views.py
from django.shortcuts import render


def homepage(request):
    # categories = Category.objects.prefetch_related('subcategories').all()
    # return render(request, 'homepage.html', {'categories': categories})
    
    return render(request, "homepage.html")
