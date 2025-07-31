from django import forms

from mainapp.models import Folder, Set


class CreateFolderForm(forms.ModelForm):
    class Meta:
        model=Folder
        fields=['name', 'description']

class CreateSetForm(forms.ModelForm):
    class Meta:
        model=Set
        fields=['name', 'type', 'description']