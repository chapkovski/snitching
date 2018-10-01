from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class EPage(Page):
    def is_displayed(self):
        return self.player.role() != 'principal'


class Intro(EPage):
    ...


class SendingMoney(EPage):
    ...


class ColsanBeliefs(Page):
    ...


class SendingBeliefs(EPage):
    ...


class Survey(Page):
    ...


class Results(Page):
    ...


page_sequence = [
    Intro,
    SendingMoney,
    ColsanBeliefs,
    SendingBeliefs,
    Survey,
    Results,
]
