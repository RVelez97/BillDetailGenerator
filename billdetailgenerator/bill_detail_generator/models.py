from django.db import models

class XMLFile(models.Model):
    file = models.FileField(upload_to='xml_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
