from django import forms


class CreateGroupForm(forms.Form):
    name = forms.CharField(label='Name of the group', max_length=50)
    type = forms.CharField(label='Type of the group', max_length=25)
    private = forms.BooleanField(label='Do you want the group to be private?', required=False)

