from django import forms

from mainapp.models import Folder


class CreateFolderForm(forms.ModelForm):
    class Meta:
        model=Folder
        fields=['name', 'description']

