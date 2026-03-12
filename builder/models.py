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

class CoverLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cv = models.ForeignKey(CV, on_delete=models.CASCADE) # Links the letter to the CV
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    generated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Letter for {self.job_title} at {self.company_name}"