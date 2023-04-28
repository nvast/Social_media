from django import forms
from .models import UserInfo


class NewPostForm(forms.Form):
    post = forms.CharField(label="",
                           max_length=1000,
                           min_length=1,
                           widget=forms.Textarea(attrs={'rows': 3,
                                                        'cols': 40,
                                                        'placeholder': 'What is on your mind?', }))


class CommentForm(forms.Form):
    comment = forms.CharField(label="",
                              max_length=1000,
                              min_length=1,
                              widget=forms.Textarea(attrs={'class': 'form-control',
                                                           'placeholder': 'Comment',
                                                           'rows': 1, }))


class ProfileInfoForm(forms.ModelForm):
    date_of_birth = forms.CharField(required=False, label='Date of birth')
    live_in = forms.CharField(required=False, label='I live in')
    phone = forms.CharField(required=False, label='Phone number')
    sex = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')], required=False, label="I'm")
    email = forms.BooleanField(required=False, label="Share email?")

    class Meta:
        model = UserInfo
        fields = ['date_of_birth', 'live_in', 'phone', 'sex', 'email']
        widgets = {
            'email': forms.CheckboxInput(),
        }


class ChatForm(forms.Form):
    message = forms.CharField(label="",
                              max_length=1000,
                              min_length=1,
                              widget=forms.Textarea(attrs={'rows': 2,
                                                           'placeholder': 'Aa', }))
