#-*- coding: utf-8 -*-;
"""Parser for site: /www.flyniki.com/.
Parser() -- main class
This modul receives flights table and returns data for all flights
"""

import requests
from lxml import html
from datetime import datetime
from datetime import timedelta

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
    get_page -- get html page.
    get_full_url -- make first request to www.flyniki.com.
    get_sesid -- get session ID for final request.
    set_ajax -- The final request for the page.
    find_data -- main func in class.
    """

    oneway = 0
    SESSION = requests.session()

    def __init__(self, departure, destination, outbound_date, return_date=''):
        self.departure = departure
        self.destination = destination
        self.outbound_date = outbound_date
        self.return_date = return_date

    def get_page(self):
        """
        This func check data format and return html page from final request: set_ajax()
        """
        self.outbound_date = self.date_error_checker(self.outbound_date)
        if self.return_date == '':
            self.oneway = 1
            self.return_date = self.outbound_date
        else:
            self.return_date = self.date_error_checker(self.return_date)
        return self.set_ajax()

    def get_full_url(self):
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

    def get_sesid(self):
        """Return url for final request snd session ID into SESSION"""
        url = 'http://www.flyniki.com/static/site/loader/' \
              'nl,js:nzf,jquery%7Cjquery.flightdatepickers,' \
              'jquery%7Cjquery.fancybox.js'
        return self.SESSION.head(url)

    def set_ajax(self):
        """ This final func makes post request and send data."""
        self.oneway = '' if not self.oneway else 'on'
        data = {'_ajax[templates][]' : ['main', 'priceoverview',
                                        'infos', 'flightinfo'],
                '_ajax[requestParams][departure]' : self.departure,
                '_ajax[requestParams][destination]' : self.destination,
                '_ajax[requestParams][returnDeparture]' : '',
                '_ajax[requestParams][returnDestination]' : '',
                '_ajax[requestParams][outboundDate]' : self.outbound_date,
                '_ajax[requestParams][returnDate]' : self.return_date,
                '_ajax[requestParams][adultCount]' : '1',
                '_ajax[requestParams][childCount]' : '0',
                '_ajax[requestParams][infantCount]' : '0',
                '_ajax[requestParams][openDateOverview]' : '',
                '_ajax[requestParams][oneway]' : self.oneway}
        response = self.SESSION.post(self.get_full_url().url, data=data)
        return response.content.replace('\\', '')

    def check_for_errors(self, page):
        errors = page.xpath('//span[@class="debugerrors"]/text()')
        if errors:
            raise Exception('Wrong ' + errors[0][1:-1] + '. Please correct your entry.')

    def date_error_checker(self, data):
    	"""This func check the date on the error and return correct one for request"""
        if len(data.split('.')) == 1:
            return data
        flight_date = datetime.strptime(data, '%d.%m.%Y')
        today = datetime.today()
        max_date = today + timedelta(days=298)
        if flight_date.date() < today.date():
            raise Exception("You enter wrong date. We can't return back")
        elif flight_date.date() > max_date.date():
            raise Exception("You enter wrong date. Out of range")
        return str(flight_date.date())

    def find_data(self):
        """ This func find data in html page."""
        page = html.fromstring(self.get_page())
        self.check_for_errors(page)
        tables = page.xpath('//div[@id="flighttables"][@class="clearfix"]/div')
        tables = tables[::2] if not self.oneway else tables[::3]
        currency = tables[0].xpath('.//th[contains(@id, "flight-table-header-price-ECO_FLEX")]/text()')[0]
        for table in tables:
            row = table.xpath('.//tbody/tr[contains(@class, "flightrow")]')
            print table.xpath('.//div[@class="vacancy_route"]/text()')[0]
            for data in row:
                start_end = ' - '.join(data.xpath('.//time/text()'))
                flight_time = data.xpath('.//span[contains(@id, "flightDurationFi_")]/text()')[0]
                price = (data.xpath('.//div[@class="lowest"]/span[contains(@id, "price")]/text()'))
                print start_end, flight_time, ' - '.join(price), currency
            print ''

    def all_price(self):
        """ all_price()
        This method get each value of the first table and inserts
        for each value of the second table.
        """
        page = html.fromstring(self.get_page())
        self.check_for_errors(page)
        price = self.extract_prices(page)
        if self.oneway:
            self.print_oneway(price)
        else:
            self.get_combined_prices(price)

    def extract_prices(self, page):
        """thos func get data from all tables on the site"""
        tables = page.xpath('//div[@id="flighttables"][@class="clearfix"]/div')[::2]
        currency = tables[0].xpath('.//th[contains(@id, "flight-table-header-price-ECO_FLEX")]/text()')[0]
        outbound_prices = {}
        inbound_prices = {}
        for ind, table in enumerate(tables):
            row = table.xpath('.//tbody/tr[contains(@class, "flightrow")]')
            for no, data in enumerate(row):
                time = ' - '.join(data.xpath('.//time/text()'))
                prices = data.xpath('.//div[@class="lowest"]/span[contains(@id, "price")]/text()')
                if not ind:
                    outbound_prices[no] = {
                        'time': time,
                        'price': prices,
                        'currency' : currency
                        }
                else:
                    inbound_prices[no] = {
                        'time': time,
                        'price': prices,
                        'currency' : currency
                    }
        return outbound_prices, inbound_prices

    def print_oneway(self, prices):
        """Return prices from oneway"""
        for key in prices[0]:
            print u'{} --- {}{}'.format(prices[0][key]['time'],
                                        ', '.join(prices[0][key]['price']),
                                        prices[0][key]['currency'])

    def get_combined_prices(self, prices):
        """Return sum of outbound_prices, inbound_prices"""
        for outbound in prices[0]:
            for i in prices[0][outbound]['price']:
                for inbound in prices[1]:
                    for j in prices[1][inbound]['price']:
                        print u'{} --- {} | {:.2f}{}'.format(prices[0][outbound]['time'],
                                                             prices[1][inbound]['time'],
                                                             float(''.join(i.split(','))) + float(''.join(j.split(','))),
                                                             prices[0][outbound]['currency'])





if __name__ == '__main__':
    E_1 = Parser('dxb', 'prg', '18.12.2016', '1.01.2017')
    # E_1.find_data()
    E_1.all_price()


