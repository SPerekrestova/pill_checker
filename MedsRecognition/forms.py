from django import forms

from MedsRecognition.models import Profile


class ImageUploadForm(forms.Form):
    image = forms.ImageField()


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["display_name", "bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "display_name": "Display Name",
            "bio": "Bio",
        }
