from django import forms
from django.forms import ModelForm, CharField, BooleanField, TextInput, CheckboxInput
from django.forms.widgets import Select, HiddenInput

from app.models import AcademicGroup


class AcademicGroupForm(ModelForm):
    """

    """
    class Meta:
        model = AcademicGroup
        fields = [
            'name', 'is_active',
        ]
        widgets = {
            'name': TextInput(attrs={'class': 'form-control academic-group'}),
            'is_active': Select(
                choices=((True, 'Yes'), (False, 'No')),
                attrs={'class': 'form-control academic-group'}
            ),
        }



# class AcademicGroupForm(ModelForm):
#     """
#
#     """
#     name = CharField(
#         label="Name",
#         widget=TextInput(attrs={'class': 'form-control academic-group'}),
#     )
#     is_active = BooleanField(
#         label="Is Active",
#         widget=ChoiceWidget(
#             attrs={'class': 'academic-group'}),
#     )
#
#     class Meta:
#         model = AcademicGroup
#         fields = [
#             'name', 'is_active',
#         ]
