from django import forms

class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop('extra', [])
        super(DynamicForm, self).__init__(*args, **kwargs)
        for field in extra_fields:
            self.fields[field] = forms.CharField()