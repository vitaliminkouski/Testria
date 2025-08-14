from django import forms

from mainapp.models import Folder, Set, Question, Block


class CreateFolderForm(forms.ModelForm):
    class Meta:
        model=Folder
        fields=['name', 'description']

class CreateSetForm(forms.ModelForm):
    class Meta:
        model=Set
        fields=['name', 'type', 'description']

class QuestionForm(forms.Form):
    text = forms.CharField(required=True, widget=forms.Textarea)
    image = forms.ImageField(required=False)

    correct_answer=forms.ChoiceField(
        label='Correct answer',
        choices=[(i, f"Answer {i}") for i in range(1, 5)],
        widget=forms.RadioSelect,
        required=True
    )


    def clean(self):
        cd=super().clean()
        text=cd.get('text')
        image=cd.get('image')
        if not (text or image):
            raise forms.ValidationError("You must fill at least one of the question fields (text or image)")
        return cd

    class Meta:
        model=Block
        fields='__all__'

class TestAnswerForm(forms.Form):
    text=forms.CharField(required=False, widget=forms.Textarea)
    image=forms.ImageField(required=False)






