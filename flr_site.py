#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser
import datetime

from elixir import session
from grab import Grab
from grab.spider import Spider, Task
from lxml.html import fromstring

import model


additional_headers = {
         'Accept-Charset': 'utf-8',
         'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'
    }


class FreeLanceRu(Spider):
    PROJECT_BY_PID = 'http://www.free-lance.ru/projects/?pid=%d'
    INDEX_BY_PAGE = 'http://www.free-lance.ru/?page=%d'

    def __init__(self, pages_count=5, *args, **kwargs):
        self.pages_count = pages_count
        super(FreeLanceRu, self).__init__(*args, **kwargs)

    def prepare(self):
        self.grab = Grab()
        self.grab.setup(headers=additional_headers)

    def get_grab(self, url=None):
        grab = self.grab.clone()
        if url:
            grab.setup(url=url)
        return grab

    def get_task(self, **kwargs):
        url = None
        if 'url' in kwargs:
            url = kwargs['url']
            del kwargs['url']
        grab = self.get_grab(url=url)
        return Task(
                grab=grab,
                **kwargs
            )

    def task_generator(self):
        for index in range(self.pages_count):
            yield self.get_task(
                    name='page',
                    url=FreeLanceRu.INDEX_BY_PAGE % (index + 1)
                )

    def task_page(self, grab, task):
        pids = grab.xpath_list('//a[starts-with(@id, "prj_name_")]/@id')
        pids = map(lambda item: int(item.split('_')[-1]), pids)
        for pid in pids:
            url = FreeLanceRu.PROJECT_BY_PID % (pid)
            if model.Project.query.filter_by(url=url).first():
                continue
            yield self.get_task(
                    name='project',
                    pid=pid,
                    url=url
                )

    def task_project(self, grab, task):
        project = None
        if grab.xpath_exists('//*[@class="contest-view"]'):
            project = self.parse_contest_view(grab, task)
        elif grab.xpath_exists('//*[@class="pay-prjct"]'):
            project = self.parse_pay_project(grab, task)
        else:
            project = self.parse_project(grab, task)

        if project:
            self.check_project(project)

    def parse_project(self, grab, task):
        project = {}
        #
        project['url'] = FreeLanceRu.PROJECT_BY_PID % (task.pid)
        #
        name = grab.xpath('//h1[@class="prj_name"]/text()')
        name = name.strip().encode('utf-8')
        project['name'] = name
        #
        date = grab.xpath('//*[@class="user-about-r"]/p/text()')
        date = date.split('[', 1)[0]
        date = date.strip().encode('utf-8')
        date = datetime.datetime.strptime(
                date,
                "%d.%m.%Y | %H:%M"
            )
        project['date'] = date
        #
        category = grab.rex(
                u'<p class="crumbs">Разделы: &#160;&#160; (.*?)(, |</p>)'
            )
        category = category.group(1)
        items = fromstring(category).xpath('./a/text()')
        if not items:
            items = category.split(' / ')
        category = items
        category = map(lambda a: a.strip().encode('utf-8'), category)
        project['category'] = category
        #
        description = grab.xpath('//*[@class="prj_text"]/text()')
        description = description.encode('utf-8')
        project['description'] = description
        #
        project['type'] = 'simple'
        #
        return project

    def parse_contest_view(self, grab, task):
        project = {}
        project['url'] = FreeLanceRu.PROJECT_BY_PID % (task.pid)
        project['type'] = 'contest'
        return project

    def parse_pay_project(self, grab, task):
        project = {}
        project['url'] = FreeLanceRu.PROJECT_BY_PID % (task.pid)
        project['type'] = 'pay'
        return project

    def check_project(self, project):
        if model.Project.query.filter_by(url=project['url']).first():
            return
        category = None
        if 'category' in project:
            category = self.get_category(project['category'])
        model.Project(
                name=project.get('name', None),
                url=project['url'],
                description=project.get('description', None),
                project_type=project['type'],
                category=category,
                date=project.get('date', None),
                site=model.free_lance_ru
            )
        session.commit()

    def get_category(self, path):
        path.reverse()
        category = None
        while path:
            category = model.Category.query.filter_by(
                    name=path.pop(),
                    parent=category,
                    site=model.free_lance_ru
                )
            category = category.first()
        return category


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
            '-g',
            '--grab',
            action="store_true",
            dest="grab",
            help=u'произвести парсинг сайта'
        )
    parser.add_option(
            '-t',
            '--threads-count',
            action="store",
            dest='threads_count',
            default=3,
            help=u'количество потоков'
        )
    parser.add_option(
            '-p',
            '--pages-count',
            action="store",
            dest='pages_count',
            default=5,
            help=u'количество страниц для извлечения ссылок'
        )
    options, args = parser.parse_args()
    if options.grab:
        freelanceru = FreeLanceRu(
                pages_count=options.pages_count,
                thread_number=options.threads_count
            )
        freelanceru.run()
    else:
        parser.print_help()
    sys.exit()
