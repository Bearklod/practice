#-*- coding: utf-8 -*-;
"""Parser for site: /www.flyniki.com/.
Parser() -- main class
This modul receives flights table and returns data for all flights
"""

import requests
from lxml import html
from datetime import datetime

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
        if flight_date.date() < today.date():
            raise Exception("You enter wrong date. We can't return back")
        if int(flight_date.strftime('%Y')) < 2016 or \
                        int(flight_date.strftime('%Y')) > 2017:
            raise Exception("Wrong date!")
        return str(flight_date.date())

    def find_data(self):
        """ This func find data in html page."""
        page = html.fromstring(self.get_page())
        self.check_for_errors(page)
        tables = page.xpath('//div[@id="flighttables"][@class="clearfix"]/div')
        tables = tables[::2] if not self.oneway else tables[::3]
        for table in tables:
            row = table.xpath('.//tbody/tr[contains(@class, "flightrow")]')
            print table.xpath('.//div[@class="vacancy_route"]/text()')[0]
            for data in row:
                start_end = ' - '.join(data.xpath('.//time/text()'))
                flight_time = data.xpath('.//span[contains(@id, "flightDurationFi_")]/text()')[0]
                price = (data.xpath('.//div[@class="lowest"]/span[contains(@id, "price")]/text()'))
                price.append('')
                print start_end, flight_time, ' gbp.  '.join(price)
            print ''

    def all_price(self):
        """ all_price()
        This method get each value of the first table and inserts
        for each value of the second table.
        """
        if not self.return_date:
            raise Exception('return data not found')
        url = self.get_full_url().url
        page = html.fromstring(self.get_page())
        self.check_for_errors(page)
        tables = page.xpath('//div[@id="flighttables"][@class="clearfix"]/div')[::2]
        row_first_table = tables[0].xpath('.//tbody/tr[contains(@class, "flightrow")]')
        row_second_table = tables[1].xpath('.//tbody/tr[contains(@class, "flightrow")]')

        for data in row_first_table:
            f_prices = data.xpath('.//div[@class="lowest"]/span[contains(@id, "price")]/text()')
            for first_price in f_prices:
                start = ' - '.join(data.xpath('.//time/text()'))
                for data in row_second_table:
                    s_prices = data.xpath('.//div[@class="lowest"]/span[contains(@id, "price")]/text()')
                    for second_prices in s_prices:
                        end = ' - '.join(data.xpath('.//time/text()'))
                        tooal_price = int(''.join(first_price[:-3].split(','))) + int(''.join(second_prices[:-3].split(',')))
                        print '{}  ---  {}  |  {:>8,}.00 gbp'.format(start, end, tooal_price)


if __name__ == '__main__':
    E_1 = Parser('dxb', 'prg', '10.12.2016', '12.12.2016')
    E_1.find_data()
    E_1.all_price()


