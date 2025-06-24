# -*- coding: utf-8 -*-

from importlib import import_module
from datetime import datetime

import requests
import pusher
from lxml import etree

from app import config, ClassProperty


class Service(object):
    _domain = None

    class InvalidDomain(Exception):
        pass

    @ClassProperty
    def domain(cls):
        if cls._domain is None:
            raise cls.InvalidDomain('You should use a specific service implementation')
        return import_module(cls._domain)


class HolidaysService(Service):
    _domain = 'app.domain'

    @classmethod
    def list_holidays(cls):
        current_year = datetime.now().year
        holidays = cls.domain.Holiday.list_all()
        if len(holidays) == 0:
            cls.domain.Holiday.fill_for_year(current_year)
            holidays = cls.domain.Holiday.list_all()
        return holidays

    @classmethod
    def get_holidays_dates(cls, year):
        url = 'http://www.calendario.com.br/api/api_feriados.php?ano={}&estado=SP&cidade=PIRACICABA&token={}'.format(year, config.HOLIDAY_TOKEN)
        response = requests.get(url)
        root = etree.fromstring(response.content)
        events = root.iter('event')
        result_dict = []
        for event_xml in events:
            event_dict = {'name': None, 'date': None, 'type_code': None}
            for props in list(event_xml):
                if props.tag in event_dict:
                    event_dict[props.tag] = props.text
            result_dict.append(event_dict)
        return result_dict


class Pusher(object):
    client = pusher.Pusher(
        app_id=config.PUSHER_APP_ID,
        key=config.PUSHER_KEY,
        secret=config.PUSHER_SECRET,
        cluster=config.PUSHER_CLUSTER,
        ssl=True
    )
    pusher_socket_id = None

    @classmethod
    def _send(cls, event, message, **data):
        if not data:
            data = {}
        data['message'] = message
        cls.client.trigger('base', event, cls._transform_key(data), cls.pusher_socket_id)

    @staticmethod
    def _snake_to_camel(name):
        result = []
        for index, part in enumerate(name.split('_')):
            if index == 0:
                result.append(part.lower())
            else:
                result.append(part.capitalize())
        return ''.join(result)

    @classmethod
    def _transform_key(cls, data):
        if isinstance(data, dict):
            return {cls._snake_to_camel(key): cls._transform_key(value) for key, value in data.items()}
        if isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, dict):
                    data[index] = {cls._snake_to_camel(key): cls._transform_key(value) for key, value in item.items()}
        return data

    @classmethod
    def send_sample(cls, **kwargs):
        cls._send('base.sample', **kwargs)
