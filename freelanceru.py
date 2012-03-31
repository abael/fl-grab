#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import datetime

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
                log_dir=options.log_dir,
                url=url
            )

    def project_generator(self):
        self.grab.request()
        tree = fromstring(self.grab.response.body)
        items = tree.xpath('/rss/channel/item/*')
        items = map(str, items)
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
            model.get_or_create(
                    model.Project,
                    name=item['title'],
                    url=item['link'],
                    description=item['description'],
                    category=self.get_or_create_category(item['category']),
                    date=datetime.datetime.strptime(
                            item['date'],
                            "%a, %d %b %Y %H:%M:%S %Z"
                        ),
                    site=self.site
                )
        session.commit()

    def get_or_create_category(self, path):
            categories = path.split('/')
            categories = map(lambda s: s.strip(), categories)
            category = None
            while len(categories):
                category = model.get_or_create(
                        model.Category,
                        name=categories.pop(),
                        parent=category,
                        site=self.site
                    )
            return category


rss = RSS(
        model.free_lance_ru,
        'http://www.free-lance.ru/rss/all.xml'
    )

try:
    while True:
        rss.update()
        print 'projects: %d, categories: %d' % (
                model.Project.query.count(),
                model.Category.query.count()
            )
        time.sleep(3)
except KeyboardInterrupt, E:
    pass

sys.exit()
