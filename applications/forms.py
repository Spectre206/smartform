from django import forms
from .models import Application
import re
from datetime import date

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'full_name', 'father_name', 'cnic_number',
            'date_of_birth', 'address', 'city', 'reason'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_cnic_number(self):
        cnic = self.cleaned_data.get('cnic_number')
        if not re.match(r'^\d{13}$', cnic):
            raise forms.ValidationError("CNIC must be exactly 13 digits.")
        return cnic

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob >= date.today():
            raise forms.ValidationError("Date of birth must be in the past.")
        if dob:
            age = (date.today() - dob).days // 365
            if age < 18:
                raise forms.ValidationError("Applicant must be at least 18 years old.")
        return dob
    
class ImageUploadForm(forms.Form):
    image = forms.ImageField()