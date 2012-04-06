#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import datetime
from optparse import OptionParser

from elixir import session
from grab import Grab
from lxml.objectify import fromstring

import options
import model


class RSS:
    def __init__(self, site, url):
        self.site = site
        self.grab = Grab()
        self.grab.setup(
                headers={'Accept-Charset': 'utf-8'},
                url=url
            )

    def project_generator(self):
        self.grab.request()
        tree = fromstring(self.grab.response.body)
        items = tree.xpath('/rss/channel/item/*')
        items = map(lambda e: e.text.encode('utf-8'), items)
        items = zip(*[items[i::6] for i in range(6)])
        for item in items:
            project = {
                    'title': item[0],
                    'link': item[1],
                    'description': item[2],
                    'category': item[4],
                    'date': item[5],
                }
            yield project

    def update(self):
        for item in self.project_generator():
            if model.Project.query.filter_by(url=item['link']).first():
                continue
            category = self.get_category(item['category'])
            model.Project(name=item['title'],
                    url=item['link'],
                    description=item['description'],
                    category=category,
                    date=datetime.datetime.strptime(
                            item['date'],
                            "%a, %d %b %Y %H:%M:%S %Z"
                        ),
                    site=self.site
                )
        session.commit()

    def get_category(self, path):
        categories = path.split(' / ')
        categories = map(lambda s: s.strip(), categories)
        categories.reverse()
        category = None
        while len(categories):
            category = model.Category.query.filter_by(
                    name=categories.pop(),
                    parent=category,
                    site=self.site
                )
            category = category.first()
        return category


def grab_free_lance_ru_rss():
    print 'Загрузка проектов из RSS...'
    rss = RSS(
            model.free_lance_ru,
            'http://www.free-lance.ru/rss/all.xml'
        )
    rss.update()
    print 'Завершено'


def grab_free_lance_ru_rss_forever(timeout):
    rss = RSS(
            model.free_lance_ru,
            'http://www.free-lance.ru/rss/all.xml'
        )
    try:
        while True:
            rss.update()
            time.sleep(rss.update())
    except KeyboardInterrupt:
        print u'Работа прервана'


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
            '-g',
            '--grab',
            action="store_true",
            dest="grab",
            help=u'произвести парсинг RSS'
        )
    parser.add_option(
            '-r',
            '--forever',
            action="store_true",
            dest="forever",
            help=u'парсить RSS бесконечно'
        )
    parser.add_option(
            '-t',
            '--timeout',
            action="store",
            dest='timeout',
            default=3,
            help=u'таймаут после проверки RSS'
        )
    options, args = parser.parse_args()
    if options.grab:
        grab_free_lance_ru_rss()
    elif options.forever:
        grab_free_lance_ru_rss_forever(enumerating=options.timeout)
    else:
        parser.print_help()
    sys.exit()
