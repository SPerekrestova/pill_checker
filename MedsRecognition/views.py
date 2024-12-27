from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from MedsRecognition.forms import ImageUploadForm
from MedsRecognition.meds_recognition import MedsRecognition
from PIL import Image
import io
import easyocr
from MedsRecognition.models import ScannedMedication  # Import the ScannedMedication model
from django.db.models import F


reader = easyocr.Reader(['en'], gpu=True)
meds_recognition = MedsRecognition()


def extract_text_with_easyocr(image):
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')

    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)

    results = reader.readtext(image_bytes.read(), detail=0)
    return " ".join(results)


@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['image']
            image = Image.open(io.BytesIO(uploaded_file.read()))
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            extracted_text = extract_text_with_easyocr(image)
            active_ingredients = recognise(extracted_text)

            # Save scanned medication to the database
            ScannedMedication.objects.create(
                user=request.user,  # Associate with the logged-in user
                medication_name="Extracted Medication",  # This can be refined as per your logic
                dosage=", ".join(active_ingredients),  # Join active ingredients into a string
                prescription_details=extracted_text,
            )

            return render(request, 'recognition/result.html',
                          {
                              'text': extracted_text,
                              'active_ingredients': active_ingredients
                          })
    else:
        form = ImageUploadForm()
    return render(request, 'recognition/upload.html', {'form': form})


@login_required
def user_dashboard(request):
    medications = ScannedMedication.objects.filter(user=request.user).order_by(F('scan_date').desc())
    return render(request, 'dashboard.html', {'medications': medications})


def recognise(extracted_text):
    active_ingredients = meds_recognition.find_active_ingredients(extracted_text)
    return list(dict.fromkeys(active_ingredients))
