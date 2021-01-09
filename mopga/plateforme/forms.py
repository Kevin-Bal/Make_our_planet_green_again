from django import forms
from django.utils.safestring import mark_safe
from .models import Evaluation

CHOICES = [
    ('0', 0), 
    ('1', 1), 
    ('2', 2),
    ('3', 3),
    ('4', 4),
    ('5', 5),
    ('6', 6),
    ('7', 7),
    ('8', 8),
    ('9', 9),
    ('10', 10)
]


class EvaluationForm(forms.ModelForm):
    note = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())
    commentaire = forms.CharField(max_length=500, widget=forms.Textarea)

    class Meta:
        model = Evaluation
        fields = ['note','commentaire']

    class Media:
        css = {
            'all': ('form_evaluation.css',)
        }


class ContactForm(forms.Form):
    contact_email = forms.EmailField(required=True)
    sujet = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

