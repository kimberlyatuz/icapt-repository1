from django.db import models

# Create your models here.
from django.db import models

class ExtractedImage(models.Model):
    image = models.ImageField(upload_to='uploaded_images/')
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"
