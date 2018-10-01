from django import forms
from .models import Player, WB, Constants
from django.forms import BaseInlineFormSet, ValidationError, inlineformset_factory
from django.core.validators import MaxValueValidator, MinValueValidator


# TODO: not sure we need formset here, no extra validation is needed - only if later on we'll check for consistency
# along threshold

# class PunishmentFormset(BaseInlineFormSet):
#     def clean(self):
#         super().clean()
#         if any(self.errors):
#             return
#         amounts = []
#         punishment_endowment = self.instance.punishment_endowment
#         for form in self.forms:
#             amounts.append(form.cleaned_data['amount'])
#         if sum(amounts) > punishment_endowment:
#             raise ValidationError(
#                 "In total you can't send more than {endowment} points!".format(
#                     endowment=punishment_endowment))

class WhistleForm(forms.ModelForm):
    CHOICES = ((False, '',), (True, '',))
    decision = forms.ChoiceField(widget=forms.RadioSelect(attrs={'required': ''}), choices=CHOICES, required=True)


WBFormset = inlineformset_factory(Player, WB,
                                  # formset=PunishmentFormset,
                                  extra=0,
                                  can_delete=False,
                                  fk_name='snitch',
                                  form=WhistleForm,
                                  fields=['decision'])
