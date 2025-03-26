from django.shortcuts import render
from .forms import DynamicForm
import sys

# Increase the recursion limit
sys.setrecursionlimit(1500)


def dynamic_form_view(request):
    if request.method == 'POST':
        form = DynamicForm(request.POST, extra=request.POST.getlist('extra_fields'))
        if form.is_valid():
            # Process the form data
            pass
    else:
        form = DynamicForm(extra=['field1', 'field2'])  # Example extra fields

    return render(request, 'app1/KimD.html', {'form': form})

def index(request):
    return render(request, 'Landing_page/index.html')

def about(request):
    return render(request, 'Landing_page/about.html')


def portfolio(request):
    return render(request, 'Landing_page/portfolio.html')

def we_do(request):
    return render(request, 'Landing_page/we_do.html')
