from django.db.models import F
from django.shortcuts import render

from MedsRecognition.decorators import supabase_login_required
from MedsRecognition.forms import ImageUploadForm
from MedsRecognition.models import Medication
from MedsRecognition.ocr_service import recognise


@supabase_login_required
def upload_image(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            active_ingredients = recognise(request)
            return render(
                request,
                "recognition/result.html",
                {
                    "active_ingredients": active_ingredients,
                },
            )
    else:
        form = ImageUploadForm()
    return render(request, "recognition/upload.html", {"form": form})


@supabase_login_required
def user_dashboard(request):
    medications = Medication.objects.filter(profile=request.auth_user).order_by(
        F("scan_date").desc()
    )
    return render(request, "recognition/dashboard.html", {"medications": medications})


def index(request):
    return render(request, "recognition/index.html")
