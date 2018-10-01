from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'Philipp Chapkovski, Valeria Maggian, Luca Corazzini. Chapkovski@gmail.com'

doc = """
First stage of a colsan study on snitching: multiple-agents-one-principal with reporting option.
"""


class Constants(BaseConstants):
    name_in_url = 'colsan_pad'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    def creating_session(self):
        # could be as well stored at session level but for the future safer at the group if we run mixed sessions
        info = self.session.config.get('info', False)
        wb = self.session.config.get('wb', False)
        for g in self.get_groups():
            g.info_treatment, g.wb_treatment = info, wb


class Group(BaseGroup):
    info_treatment = models.BooleanField()
    wb_treatment = models.BooleanField()


class Player(BasePlayer):
    def role(self):
        if self.id_in_group == 1:
            return 'principal'
        return 'employee'
