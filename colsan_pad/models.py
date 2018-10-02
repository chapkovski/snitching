from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

author = 'Philipp Chapkovski, Valeria Maggian, Luca Corazzini. Chapkovski@gmail.com'

doc = """
First stage of a colsan study on snitching: multiple-agents-one-principal with reporting option.
"""


class Constants(BaseConstants):
    name_in_url = 'colsan_pad'
    players_per_group = 4  # todo: in prod to 4
    num_rounds = 1
    pun_coef = 2  # coefficient for punishment by a principal
    worker_wage = 100  # todo: keep in currency?
    cost_effort_table = {0: 0, 1: 5, 2: 12, 3: 18, 4: 24, 5: 35, 6: 42, 7: 56, }
    max_punishment = 10  # todo: limit it somehow in total
    principal_endowment = 200
    principal_coef = 10


class Subsession(BaseSubsession):
    def creating_session(self):
        # could be as well stored at session level but for the future safer at the group if we run mixed sessions
        info = self.session.config.get('info', False)
        wb = self.session.config.get('wb', False)
        for g in self.get_groups():
            g.info_treatment, g.wb_treatment = info, wb
            g.chosen_snitch = random.randint(2, Constants.players_per_group)
            for w in g.get_workers():
                w.worker_id = w.id_in_group - 1
                # todo: optimize later with bulk_create
                for o in w.get_other_workers():
                    for c in Constants.cost_effort_table.keys():
                        w.wbs.create(target=o, effort=c)


class Group(BaseGroup):
    chosen_snitch = models.IntegerField(doc='id of worker whose WB decision will be implemented')
    info_treatment = models.BooleanField()
    wb_treatment = models.BooleanField()

    def get_workers(self):
        return [p for p in self.get_players() if p.role() == 'worker']

    def total_performance(self):
        # todo: get rid of or 0 in prod
        return sum([p.effort or 0 for p in self.get_workers()])

    def set_payoffs(self):
        # todo: increase group size to 4 (3 workers one principal); in dev use 3 players (2 w., one 1pr).
        principal, workers = self.get_player_by_role('principal'), self.get_workers()
        principal.payoff = self.principal_payoff()
        for w in workers:
            w.payoff = w.worker_payoff()

    def total_punishment(self):
        tot_punishments = [getattr(self, 'punishment_worker_{}'.format(i)) for i in
                           range(1, Constants.players_per_group)]
        return sum(tot_punishments)

    def principal_payoff(self):
        # TODO: store wage in player field
        tot_wages = sum([Constants.worker_wage for w in self.get_workers()])

        return Constants.principal_endowment - \
               tot_wages + self.total_performance() * \
                           Constants.principal_coef \
               - self.total_punishment()


class Player(BasePlayer):
    # todo: check for NO initials in prod.
    effort = models.IntegerField(doc='storing individual efforts by workers', label='Please choose the effort level',
                                 widget=widgets.RadioSelectHorizontal,
                                 )

    wb = models.BooleanField(doc='snitching decision by a worker')
    worker_id = models.IntegerField()

    def get_other_workers(self):
        return [w for w in self.group.get_workers() if w != self]

    def get_punishment_field_name(self):
        return 'punishment_worker_{}'.format(self.worker_id)

    def get_effort_level_for_p(self):
        chosen_snitch = self.group.get_player_by_id(self.group.chosen_snitch)
        try:
            snitch_wb_on_ego = WB.objects.get(snitch=chosen_snitch, effort=self.effort, target=self,
                                              decision__isnull=False)
            if snitch_wb_on_ego.decision:
                return self.effort
        except WB.DoesNotExist:
            return 'Unknown'

    def get_punishment_received(self):
        return getattr(self.group, 'punishment_worker_{}'.format(self.worker_id)) * Constants.pun_coef

    def role(self):
        if self.id_in_group == 1:
            return 'principal'
        return 'worker'

    def worker_payoff(self):
        # todo: store endowments in player level for future individualization
        return Constants.worker_wage - Constants.cost_effort_table[self.effort] - self.get_punishment_received()

        # TODO: move it into custom model without this BS.


# TODO: NB!!! add a slightly different payoff as STAGE 2


for i in range(1, Constants.players_per_group):
    Group.add_to_class('punishment_worker_{}'.format(i), models.IntegerField(min=0,
                                                                             max=Constants.max_punishment))

from django.db import models as djmodels


class WB(djmodels.Model):
    snitch = djmodels.ForeignKey(to=Player, related_name='wbs')
    target = djmodels.ForeignKey(to=Player, related_name='donos')
    effort = models.IntegerField()
    decision = models.BooleanField(doc='to snitch or not for this level of effort',
                                   null=True,
                                   widget=widgets.RadioSelectHorizontal,
                                   )
