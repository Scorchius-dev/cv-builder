from django.shortcuts import render
from .models import CV
from .services import generate_cover_letter


def index(request):
    letter = None
    cvs = CV.objects.all()  # Get all saved CVs to show in a dropdown

    if request.method == "POST":
        cv_id = request.POST.get("cv_id")
        job_description = request.POST.get("job_description")

        # 1. Get the specific CV data
        selected_cv = CV.objects.get(id=cv_id)
        cv_text = (
            f"Skills: {selected_cv.skills}\n"
            f"Experience: {selected_cv.experience}"
        )

        # 2. Call our AI service
        letter = generate_cover_letter(cv_text, job_description)

    return render(
        request,
        "builder/index.html",
        {"cvs": cvs, "letter": letter},
    )
