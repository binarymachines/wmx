#!/usr/bin/env python

import os, sys
import json
import copy
from mercury.base_classes import JSONDocToCSVConverter
from snap import common
import collections


class ForecastConverter(JSONDocToCSVConverter):

    def get_field_names(self, jsondata, **kwargs):
        return [
            'zipcode',
            'date',
            'maxtemp_f',
            'mintemp_f',
            'avgtemp_f',
            'daily_chance_of_rain',
            'daily_chance_of_snow',
            'condition.text',
            'condition.icon'
        ]
        

    def scan(self, json_document, field_names, **kwargs):

        for i in range(2):
            output_record = dict()
            
            output_record['zipcode'] = kwargs.get('zipcode')
            output_record['date'] = json_document['forecast']['forecastday'][0]['date']
            output_record['maxtemp_f'] = json_document['forecast']['forecastday'][0]['day']['maxtemp_f']
            output_record['mintemp_f'] = json_document['forecast']['forecastday'][0]['day']['mintemp_f']
            output_record['avgtemp_f'] = json_document['forecast']['forecastday'][0]['day']['avgtemp_f']
            output_record['daily_chance_of_rain'] = json_document['forecast']['forecastday'][0]['day']['daily_chance_of_rain']
            output_record['daily_chance_of_snow'] = json_document['forecast']['forecastday'][0]['day']['daily_chance_of_snow']
            output_record['condition.text'] = json_document['forecast']['forecastday'][0]['day']['condition']['text']
            output_record['condition.icon'] = json_document['forecast']['forecastday'][0]['day']['condition']['icon']

            yield output_record


class HourlyForecastConverter(JSONDocToCSVConverter):

    def get_field_names(self, jsondata, **kwargs):
        return [
            'zipcode',
            'date',
            'time',
            'temp_f',
            'feelslike_f',
            'heatindex_f',
            'windchill_f',
            'humidity',
            'cloud',
            'chance_of_rain',
            'chance_of_snow',
            'condition.text',
            'condition.icon'
        ]

    def scan(self, json_document, field_names, **kwargs):

        for hourly_data in json_document['forecast']['forecastday'][0]['hour']:

            output_record = dict()

            output_record['zipcode'] = kwargs.get('zipcode')
            output_record['date'] = kwargs.get('date').lstrip('(').rstrip(')')
            output_record['time'] = hourly_data['time'].lstrip('(').rstrip(')')

            temp_f = float(hourly_data['temp_f'])
            output_record['temp_f'] = str(temp_f)

            output_record['feelslike_f'] = hourly_data['feelslike_f']
            output_record['heatindex_f'] = hourly_data['heatindex_f']
            output_record['windchill_f'] = hourly_data['windchill_f']
            output_record['humidity'] = hourly_data['humidity']
            output_record['cloud'] = hourly_data['cloud']
            output_record['chance_of_rain'] = hourly_data['chance_of_rain']
            output_record['chance_of_snow'] = hourly_data['chance_of_snow']

            output_record['condition.text'] = hourly_data['condition']['text']
            output_record['condition.icon'] = hourly_data['condition']['icon']

            yield output_record