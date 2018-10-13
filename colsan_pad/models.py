from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
from django.db import models as djmodels

author = 'Philipp Chapkovski, Valeria Maggian, Luca Corazzini. Chapkovski@gmail.com'

doc = """
A colsan study on snitching: multiple-agents-one-principal with reporting option.
Stage 2 whose announcement serves as a deterrence of snitching is the same game with slightly different payoff structure
"""


class Constants(BaseConstants):
    name_in_url = 'colsan_pad'
    players_per_group = 3  # todo: in prod to 4
    workers_per_group = players_per_group - 1
    num_rounds = 2
    num_s1_rounds = 1  # for how many rounds we play stage 1 first
    num_s2_rounds = num_rounds-num_s1_rounds
    stage1_rounds = range(1, num_s1_rounds + 1)
    stage2_rounds = range(num_s1_rounds, num_rounds + 1)

    pun_coef = 2  # coefficient for punishment by a principal
    worker_wage = c(100)
    cost_effort_table = {0: 0, 1: 5, 2: 12, 3: 18, 4: 24, 5: 35, 6: 42, 7: 56, }
    max_punishment = 10  # todo: limit it somehow in total
    principal_endowment = c(worker_wage * workers_per_group)
    principal_coef = 10
    stage2_principal_payoff = c(0)  # at stage 2 Principal gets a fixed payoff (0?)


class Subsession(BaseSubsession):
    def creating_session(self):
        # could be as well stored at session level but for the future safer at the group if we run mixed sessions
        info = self.session.config.get('info', False)
        wb = self.session.config.get('wb', False)
        for g in self.get_groups():
            # TODO: writing a mechanism to change instructions based on stage and payoff function
            # the built-in block in WOrkerDecision should be substituted too
            g.stage = 1 if self.round_number in Constants.stage1_rounds else 2
            g.is_first_round_stage = self.round_number in [Constants.stage1_rounds[0], Constants.stage2_rounds[0]]
            g.info_treatment, g.wb_treatment = info, wb
            g.chosen_snitch = random.randint(2, Constants.players_per_group)
            p, ws = g.get_player_by_role('principal'), g.get_workers()
            p.endowment = Constants.principal_endowment
            for w in ws:
                w.endowment = Constants.worker_wage
                w.worker_id = w.id_in_group - 1
                # todo: optimize later with bulk_create
                for o in w.get_other_workers():
                    for c in Constants.cost_effort_table.keys():
                        w.wbs.create(target=o, effort=c)


class Group(BaseGroup):
    chosen_snitch = models.IntegerField(doc='id of worker whose WB decision will be implemented')
    info_treatment = models.BooleanField()
    wb_treatment = models.BooleanField()
    stage = models.IntegerField(doc='to understand what stage we are in: 1 or 2')
    is_first_round_stage = models.BooleanField(doc='whether this round is the first one in each stage')

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

    def stage1_principal_payoff(self):
        p = self.get_player_by_role('principal')
        tot_wages = sum([w.endowment for w in self.get_workers()])
        # right now p.endowment = tot_wages but later on we may wish to change that
        return (p.endowment
                - tot_wages
                + self.total_performance() * Constants.principal_coef
                - self.total_punishment())

    def stage2_principal_payoff(self):
        # at stage 2 Principal gets a fixed payoff (0?)
        return Constants.stage2_principal_payoff

    def principal_payoff(self):
        return getattr(self, 'stage{}_principal_payoff'.format(self.stage))()


class Player(BasePlayer):
    # todo: check for NO initials in prod.
    effort = models.IntegerField(doc='storing individual efforts by workers', label='Please choose the effort level',
                                 widget=widgets.RadioSelectHorizontal,
                                 )

    wb = models.BooleanField(doc='snitching decision by a worker')
    worker_id = models.IntegerField()
    endowment = models.CurrencyField(doc='endowment get by each player in the beginning')

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
            else:
                return 'Unknown'
        except WB.DoesNotExist:
            return 'Unknown'

    def get_punishment_received(self):
        return getattr(self.group, 'punishment_worker_{}'.format(self.worker_id)) * Constants.pun_coef

    def role(self):
        if self.id_in_group == 1:
            return 'principal'
        return 'worker'

    def stage1_worker_payoff(self):
        return self.endowment - Constants.cost_effort_table[self.effort] - self.get_punishment_received()

    def stage2_worker_payoff(self):
        other_w_efforts = c(sum([o.effort for o in self.get_other_workers()]))
        return self.endowment - Constants.cost_effort_table[self.effort] + other_w_efforts * Constants.principal_coef

    def worker_payoff(self):
        return getattr(self, 'stage{}_worker_payoff'.format(self.group.stage))()

    def effort_by_others(self):
        return sum([o.effort for o in self.get_other_workers()])


# TODO: move punishment info into custom model without this BS.
for i in range(1, Constants.players_per_group):
    Group.add_to_class('punishment_worker_{}'.format(i), models.IntegerField(min=0,
                                                                             max=Constants.max_punishment))


class WB(djmodels.Model):
    snitch = djmodels.ForeignKey(to=Player, related_name='wbs')
    target = djmodels.ForeignKey(to=Player, related_name='donos')
    effort = models.IntegerField()
    decision = models.BooleanField(doc='to snitch or not for this level of effort',
                                   null=True,
                                   widget=widgets.RadioSelectHorizontal,
                                   )
