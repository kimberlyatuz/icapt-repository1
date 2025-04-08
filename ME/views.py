from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import pytesseract
from PIL import Image
from .models import ExtractedImage
from .forms import ExtractedImageForm

# Create your views here.

def back_up(request):
    return render(request, 'app1/admin_users_backup.html')

def base(request):
    return render(request, 'app1/base.html')

def user_settings_management(request):
    return render(request, 'app1/admin_users_settings.html')

def user_reports(request):
    return render(request, 'app1/admin_users_reports.html')

def user_form_management(request):
    return render(request, 'app1/admin_user_form_management.html')

def users_management(request): #
    return render(request, 'app1/admin_users_usermanagement.html')

def patients_management(request):
    return render(request, 'app1/admin_users_patients.html')

def users(request):
    return render(request, 'app1/admin_users_users.html')

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def upload_and_extract(request):
    if request.method == "POST":
        form = ExtractedImageForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save(commit=False)
            image = Image.open(uploaded_image.image)
            uploaded_image.extracted_text = pytesseract.image_to_string(image)
            uploaded_image.save()
            return redirect('result', pk=uploaded_image.pk)
    else:
        form = ExtractedImageForm()
    return render(request, 'upload.html', {'form': form})

def result_view(request, pk):
    image_entry = ExtractedImage.objects.get(pk=pk)
    return render(request, 'result.html', {'image_entry': image_entry})



