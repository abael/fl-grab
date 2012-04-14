#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

import model


def print_projects(start=None, count=None, show_url=False,
                   show_date=False, show_description=False,
                   enumeration=False):
    projects = model.Project.query
    projects = projects.filter_by(project_type='simple')
    projects = projects.order_by(model.Project.id.desc())
    if start:
        projects = projects.offset(start)
    if count:
        projects = projects.limit(count)
    for project in projects:
        print '%s%s%s%s' % (
                '%d: ' % (project.id) if enumeration else '',
                project.name,
                ' [%s]' % (project.date) if show_date else '',
                ' [%s]' % (project.url) if show_url else ''
            )
        #print '%d: %s [%s]' % (project.id, project.name, project.url)


def print_information():
    print 'Проектов: %d' % (
            model.Project.query.count()
        )


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
            '-i',
            '--information',
            action="store_true",
            dest="information",
            help=u'показать статистику проектов'
        )
    parser.add_option(
            '-e',
            '--enumeration',
            action="store_true",
            dest="enumeration",
            help=u'показывать коды проектов'
        )
    parser.add_option(
            '-d',
            '--date',
            action="store_true",
            dest="show_date",
            help=u'показывать дату проекта'
        )
    parser.add_option(
            '-u',
            '--url',
            action="store_true",
            dest="show_url",
            help=u'показывать URL проекта'
        )
    parser.add_option(
            '-s',
            '--start',
            action="store",
            dest='start',
            default=0,
            help=u'порядковый номер с которого начинать вывод'
        )
    parser.add_option(
            '-c',
            '--count',
            action="store",
            dest='count',
            default=30,
            help=u'количество выводимых проектов'
        )
    options, args = parser.parse_args()
    if options.information:
        print_information()
    else:
        print_projects(
                start=options.start,
                count=options.count,
                show_date=options.show_date,
                show_url=options.show_url,
                enumeration=options.enumeration
            )
    sys.exit()
