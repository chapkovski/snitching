from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from .forms import WBFormset


class Stage1Page(Page):
    _allow_custom_attributes = True

    def extra_is_displayed(self):
        return True

    def is_displayed(self):
        return self.group.stage == 1 and self.extra_is_displayed()


class Intro(Page):
    # todo: later on move intro and results under one umbrella to deal with dynamic template names
    _allow_custom_attributes = True

    def get_template_names(self):
        return ['colsan_pad/InstructionsStage{}.html'.format(self.group.stage)]

    def is_displayed(self):
        # we don't show instructions to a Principal at stage 2 (because he skips everything)
        return not (self.group.stage == 2 and self.player.role() == 'principal')


class IntroInfo(Stage1Page):
    def extra_is_displayed(self):
        return self.group.info_treatment and self.player.role() == 'worker'


class WorkerDecision(Page):
    def is_displayed(self):
        return self.player.role() == 'worker'

    form_model = 'player'
    form_fields = ['effort']

    def effort_choices(self):
        return sorted(list(Constants.cost_effort_table.keys()))


class AfterEffortWP(WaitPage):
    ...


class WBDecision(Stage1Page):
    _allow_custom_attributes = True

    def extra_is_displayed(self):
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


class PWaitingForSnitchersWP(WaitPage):
    ...


class PrincipalPunishment(Stage1Page):
    form_model = 'group'

    def extra_is_displayed(self):
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
    _allow_custom_attributes = True

    def get_template_names(self):
        return ['colsan_pad/Stage{}Results.html'.format(self.group.stage)]

    def vars_for_template(self):
        if self.player.role() == 'worker':
            return {'cost_of_effort': Constants.cost_effort_table[self.player.effort]}


page_sequence = [
    Intro,
    IntroInfo,
    WorkerDecision,
    AfterEffortWP,
    WBDecision,
    PWaitingForSnitchersWP,
    PrincipalPunishment,
    BeforeResultsWP,
    Results,
]
