from django.contrib import admin
from .models import CV, CoverLetter # This imports both of your blueprints

# This tells the dashboard to display both sections
admin.site.register(CV)
admin.site.register(CoverLetter)
