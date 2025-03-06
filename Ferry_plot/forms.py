from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
