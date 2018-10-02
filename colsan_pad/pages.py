from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Intro(Page):
    ...


class IntroInfo(Page):
    def is_displayed(self):
        return self.group.info_treatment


class WorkerDecision(Page):
    def is_displayed(self):
        return self.player.role() == 'worker'

    form_model = 'player'
    form_fields = ['effort']

    def effort_choices(self):
        return sorted(list(Constants.cost_effort_table.keys()))


class AfterEffortWP(WaitPage):
    ...

from .forms import WBFormset


class WBDecision(Page):
    _allow_custom_attributes = True

    def is_displayed(self):
        return self.group.wb_treatment and self.player.role() == 'worker'

    def vars_for_template(self):
        return {'formset': WBFormset(instance=self.player)}

    def post(self):
        context = super().get_context_data()

        formset = WBFormset(self.request.POST, instance=self.player)
        context['formset'] = formset
        context['form'] = self.get_form()
        if formset.is_valid():
            # do we need allwbs??
            allwbs = formset.save(commit=True)
        else:
            return self.render_to_response(context)
        return super().post()
        # form_model = 'player'
        # form_fields = ['wb']


class PWaitingForSnitchersWP(WaitPage):
    ...


class PrincipalPunishment(Page):
    form_model = 'group'

    def is_displayed(self):
        return self.player.role() == 'principal'

    def vars_for_template(self):
        frm = self.get_form()
        data = zip(frm, self.group.get_workers())
        return {'data': data}

    def get_form_fields(self):
        return ['punishment_worker_{}'.format(i.worker_id) for i in self.group.get_workers()]


class BeforeResultsWP(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(Page):
    def vars_for_template(self):
        if self.player.role()=='worker':
            return {'cost_of_effort': Constants.cost_effort_table[self.player.effort]}


page_sequence = [
    # Intro,
    # IntroInfo,
    # WorkerDecision,
    # AfterEffortWP,
    WBDecision,
    # PWaitingForSnitchersWP,
    # PrincipalPunishment,
    # BeforeResultsWP,
    # Results,
]
