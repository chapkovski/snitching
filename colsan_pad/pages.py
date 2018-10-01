from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Intro(Page):
    ...


class IntroInfo(Page):
    ...


class EmployeeDecision(Page):
    ...


class WBDecision(Page):
    ...


class PrincipalPunishment(Page):
    ...


page_sequence = [
    Intro,
    IntroInfo,
    EmployeeDecision,
    WBDecision,
    PrincipalPunishment,

]
