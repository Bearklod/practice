# -*- coding: utf-8 -*-;
"""Parser for site: /www.flyniki.com/. 
Parser() -- main class
This modul receives flights table and returns data for all flights
"""

import re
import requests
from lxml import html
from datetime import datetime, timedelta


class Parser(object):

    """class Parser

    Keyword arguments:
    departure -- IATA code.
    destination -- IATA code.
    outbound_date -- departure date (day.month.year  or year-month-day).
    if the day or month are less than 10, then put a '0' in front like '01'
    return_date -- (default '').
    Functions:
    __init__
    get_search_results -- get html page.
    send_first_request -- make first request to www.flyniki.com.
    get_ses_id -- get session ID for final request.
    get_fare_info -- main func in class.
    """

    oneway = 0
    SESSION = requests.session()

    def __init__(self):
        """ The class constructor has 4 args entered from the keyboard"""
        self.departure = self.check_IATA(raw_input('Departure plase (IATA code): '))
        self.destination = self.check_IATA(raw_input('Destination plase (IATA code): '))
        self.outbound_date = self.date_error_checker(raw_input('Departure date (day.month.year): '))
        self.return_date = raw_input('Return date (day.month.year): ')
        if self.return_date == '':
            self.oneway = 1
            self.return_date = self.outbound_date
        else:
            self.return_date = self.date_error_checker(self.return_date)

    def check_IATA(self, IATA):
        """ check_IATA codes"""
        if re.match(r'^[a-z]{3}$', IATA, re.IGNORECASE):
            return IATA
        else:
            raise Exception('Wrong IATA code')

    def send_first_request(self):
        """
        hit func makes first get request with params to www.flyniki.com
        """
        url = 'http://www.flyniki.com/en/booking/flight/vacancy.php?'
        params = {'departure': self.departure,
                  'destination': self.destination,
                  'outbound_date': self.outbound_date,
                  'return_date': self.return_date,
                  'oneway': self.oneway,
                  'openDateOverview': '0',
                  'adultCount': '1',
                  'childCount': '0',
                  'infantCount': '0'}
        return self.SESSION.get(url, params=params)

    def get_ses_id(self):
        """Return url for final request snd session ID into SESSION"""
        url = 'http://www.flyniki.com/static/site/loader/' \
              'nl,js:nzf,jquery%7Cjquery.flightdatepickers,' \
              'jquery%7Cjquery.fancybox.js'
        return self.SESSION.head(url)

    def get_search_results(self):
        """ This final func makes post request and send ajax data."""
        self.oneway = '' if not self.oneway else 'on'
        data = {'_ajax[templates][]': ['main', 'priceoverview', 'infos', 'flightinfo'],
                '_ajax[requestParams][departure]': self.departure,
                '_ajax[requestParams][destination]': self.destination,
                '_ajax[requestParams][returnDeparture]': '',
                '_ajax[requestParams][returnDestination]': '',
                '_ajax[requestParams][outboundDate]': self.outbound_date,
                '_ajax[requestParams][returnDate]': self.return_date,
                '_ajax[requestParams][adultCount]': '1',
                '_ajax[requestParams][childCount]': '0',
                '_ajax[requestParams][infantCount]': '0',
                '_ajax[requestParams][openDateOverview]': '',
                '_ajax[requestParams][oneway]': self.oneway}
        response = self.SESSION.post(self.send_first_request().url, data=data)
        return response.content.replace('\\', '')

    @staticmethod
    def check_for_errors(page):
        errors = page.xpath('//span[@class="debugerrors"]/text()')
        if errors:
            raise Exception('Wrong ' + errors[0][1:-1] + '. Please correct your entry.')
        elif page.xpath('//div[@id="flighttables"][@class="clearfix"]/div') == []:
            raise Exception('No connections found for the entered data.')
        return page

    @staticmethod
    def date_error_checker(data):
        """
        This func check the date on the error
        and return correct one for request
        """
        flight_date = datetime.strptime(data, '%d.%m.%Y')
        today = datetime.today()
        max_date = today + timedelta(days=298)
        if flight_date.date() < today.date():
            raise Exception("You enter wrong date. We can't return back")
        elif flight_date.date() > max_date.date():
            raise Exception("There are no tickets on this day. Please use an earlier date")
        return flight_date.date()

    def get_fare_info(self):
        """ get_fare_info()
        This method get each value of the first table and inserts
        for each value of the second table.
        """
        page = html.fromstring(self.get_search_results())
        self.check_for_errors(page)
        price = self.extract_prices(page)
        if self.oneway:
            self.print_oneway(price['outbound'])
        else:
            self.get_combined_prices(price)

    @staticmethod
    def extract_prices(page):
        """this func get data from all tables on the site"""
        tables = page.xpath('//div[@id="flighttables"][@class="clearfix"]/div')[::2]
        currency = tables[0].xpath('.//th[contains(@id, "flight-table-header-price-")]/text()')[0]
        all_prices = {'outbound': [], 'inbound': []}

        for ind, table in enumerate(tables):
            row = table.xpath('.//tbody/tr[contains(@class, "flightrow")]')
            for data in row:
                time = ' - '.join(data.xpath('.//time/text()'))
                prices = data.xpath('.//div[@class="lowest"]/span[contains(@id, "price")]/text()')
                if not ind:
                    all_prices['outbound'].append({
                        'time': time,
                        'price': prices,
                        'currency': currency
                        })
                else:
                    all_prices['inbound'].append({
                        'time': time,
                        'price': prices,
                        'currency': currency
                        })
        return all_prices

    @staticmethod
    def print_oneway(prices):
        """Return prices from oneway"""
        for price in prices:
            print u'{} --- {} {}'.format(price['time'], ' - '.join(price['price']), price['currency'])

    @staticmethod
    def get_combined_prices(prices):
        """Return sum of outbound_prices, inbound_prices"""
        for out_flight in prices['outbound']:
            for out_price in out_flight['price']:
                for in_flight in prices['inbound']:
                    for in_price in in_flight['price']:
                        print u'{} --- {}  |  {:.2f} {}'.format(out_flight['time'], in_flight['time'],
                                                                float(''.join(out_price.split(','))) +
                                                                float(''.join(in_price.split(','))),
                                                                in_flight['currency'])


if __name__ == '__main__':
    E_1 = Parser()
    E_1.get_fare_info()
