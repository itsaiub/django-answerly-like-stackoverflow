from django import forms
from django.contrib.auth import get_user_model

from . import models


class QuestionForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=get_user_model().objects.all(),
        disabled=True
    )

    class Meta:
        model = models.Question
        fields = ['title', 'question', 'user', ]


class AnswerForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=get_user_model().objects.all(),
        disabled=True,
    )

    question = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=models.Question.objects.all(),
        disabled=True,
    )

    class Meta:
        model = models.Answer
        fields = ['answer', 'user', 'question', ]
