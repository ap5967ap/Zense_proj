from django import forms
from .models import IncomeObject
from bootstrap_datepicker_plus.widgets import DatePickerInput
class IncomeAdd(forms.ModelForm):
    '''Form to add income'''
    class Meta:
        model=IncomeObject
        fields=('source','amount','frequency','last_date','status','description')
        widgets={
            'last_date':DatePickerInput(),
        }
        def __init__(self) -> None:
            for f in self.fields:
                self.fields[f].widget.attrs['class']='form-control'
                self.fields[f].widget.attrs['placeholder']=f.capitalize()
                self.fields[f].label=''
                self.fields[f].help_text=''
                self.fields[f].required=True
            self.fields['description'].widget.attrs['rows']=3
            self.fields['description'].required=False
            