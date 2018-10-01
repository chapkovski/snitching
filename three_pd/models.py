from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Philipp Chapkovski, Valeria Maggian, Luca Corazzini'

doc = """
Second stage of a colsan study on snitching: three-players Prisoner's Dilemma
"""


class Constants(BaseConstants):
    name_in_url = 'three_pd'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    def role(self):
        return self.participant.colsan_pad_player.all().first().role()
