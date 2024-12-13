import io
from django.shortcuts import render
from MedsRecognition.forms import ImageUploadForm
from MedsRecognition.meds_recognition import MedsRecognition
from PIL import Image
import easyocr

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
            return render(request, 'recognition/result.html',
                          {
                              'text': extracted_text,
                              'active_ingredients': active_ingredients
                           })
    else:
        form = ImageUploadForm()
    return render(request, 'recognition/upload.html', {'form': form})


def recognise(extracted_text):
    active_ingredients = meds_recognition.find_active_ingredients(extracted_text)
    return active_ingredients