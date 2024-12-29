import io

import easyocr
from PIL import Image
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, redirect

from MedsRecognition.auth_service import sign_up_user, sign_in_user
from MedsRecognition.forms import ImageUploadForm
from MedsRecognition.meds_recognition import MedsRecognition
from MedsRecognition.models import ScannedMedication
from MedsRecognition.supabase_client import get_supabase_client

reader = easyocr.Reader(['en'], gpu=True)
meds_recognition = MedsRecognition()
User = get_user_model()
supabase = get_supabase_client()


def extract_text_with_easyocr(image):
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')

    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)

    results = reader.readtext(image_bytes.read(), detail=0)
    return " ".join(results)


def supabase_signup_view(request):
    """
    A view to sign up a new user using Supabase auth.
    We also create a local Django user record so we can manage sessions easily.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username', email)  # or any logic you prefer

        # 1) Sign up with Supabase
        try:
            result = sign_up_user(email, password)

            # If sign_up is successful, Supabase returns user data with an "id" or "user" field
            if result and result.user:
                supabase_user_id = result.user.id

                # 2) Create or update local Django user
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username,
                        'supabase_user_id': supabase_user_id
                    }
                )

                if not created:
                    # If user already exists, update the supabase_user_id if missing
                    if not user.supabase_user_id:
                        user.supabase_user_id = supabase_user_id
                        user.save()
                django_login(request, user)
                messages.success(request, "Signed up and logged in successfully.")
                return redirect('dashboard')  # or wherever
            else:
                messages.error(request, "Sign-up failed. Check your email/password.")
        except Exception as e:
            messages.error(request, f"Sign-up error: {e}")

    return render(request, 'recognition/signup.html')


def supabase_login_view(request):
    """
    A view that authenticates with Supabase, then logs in user via Django session.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # 1) Sign in with Supabase
            result = sign_in_user(email, password)
            if result and result.user:
                # 2) Find local Django user
                local_user = User.objects.filter(email=email).first()
                if local_user:
                    # 3) Use Django's session-based login
                    login(request, local_user)
                    messages.success(request, "Successfully logged in!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "No local user found. Please sign up.")
            else:
                messages.error(request, "Invalid credentials or login failed.")
        except Exception as e:
            messages.error(request, f"Supabase login error: {e}")
    return render(request, 'recognition/login.html')


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
    return render(request, 'recognition/dashboard.html', {'medications': medications})


def recognise(extracted_text):
    active_ingredients = meds_recognition.find_active_ingredients(extracted_text)
    return list(dict.fromkeys(active_ingredients))
