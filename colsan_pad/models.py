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
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    def role(self):
        if self.id_in_group == 1:
            return 'principal'
        return 'employee'
