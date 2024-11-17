# views.py
from django.shortcuts import render
# from .models import Subcategory, ServiceSession, Worker, Testimonial


def homepage(request):
    return render(request, "homepage.html")



def subcategory_worker(request):
    # subcategory = Subcategory.objects.get(id=subcategory_id)
    # sessions = ServiceSession.objects.filter(subcategory=subcategory)
    # workers = Worker.objects.all()  # Adjust this as per your requirements
    # testimonials = Testimonial.objects.filter(worker__in=workers)

    context = {
        # 'subcategory': subcategory,
        # 'sessions': sessions,
        # 'workers': workers,
        # 'testimonials': testimonials,
        "is_worker": True,
    }
    return render(request, "subcategory_worker.html", context)

def subcategory_user(request):
    # subcategory = Subcategory.objects.get(id=subcategory_id)
    # sessions = ServiceSession.objects.filter(subcategory=subcategory)
    # workers = Worker.objects.all()  # Adjust this as per your requirements
    # testimonials = Testimonial.objects.filter(worker__in=workers)

    context = {
        # 'subcategory': subcategory,
        # 'sessions': sessions,
        # 'workers': workers,
        # 'testimonials': testimonials,
        "is_worker": False,
    }
    return render(request, "subcategory_user.html", context)

# views.py
from django.shortcuts import render

def order(request):
    return render(request, 'order.html')  # Change path if you use project-level templates


