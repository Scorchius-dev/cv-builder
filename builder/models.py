from django.db import models
from django.contrib.auth.models import User

class CV(models.Model):
    # This links the CV to the user who created it
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # The actual content of the CV
    title = models.CharField(max_length=100, help_text="e.g., Software Engineer CV")
    education = models.TextField()
    experience = models.TextField()
    skills = models.TextField()

    def __str__(self):
        return f"{self.user.username}'s CV: {self.title}"