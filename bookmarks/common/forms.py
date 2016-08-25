from django import forms


class BootStrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootStrapForm, self).__init__(*args, **kwargs)

        # Add bootstrap classes:
        for field in self.fields:
            checkbox_fields = [
                forms.CheckboxInput,
                forms.CheckboxSelectMultiple,
            ]
            if type(self.fields[field].widget) not in checkbox_fields:
                self.fields[field].widget.attrs['class'] = 'form-control'
