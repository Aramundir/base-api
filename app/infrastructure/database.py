# -*- coding: utf-8 -*-
from sqlalchemy_utils.types import choice


class AppRepository(object):
    db = None


HOLIDAY_TYPE = [
    ('N', 'National'),
    ('S', 'State'),
    ('M', 'Municipal'),
    ('O', 'Optional'),
]


class HolidayType(choice.ChoiceType):
    def __init__(self):
        super(HolidayType, self).__init__(HOLIDAY_TYPE)

    def __repr__(self):
        return "HolidayType()"
