#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

import model


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
            '-p',
            '--drop-projects',
            action="store_true",
            dest="projects",
            help=u'удалить все проекты из БД'
        )
    parser.add_option(
            '-d',
            '--drop-database',
            action="store_true",
            dest="database",
            help=u'пересоздать БД'
        )
    options, args = parser.parse_args()
    if options.database:
        print u'Пересоздание БД'
        model.drop_database()
        print u'Готово'
        print u'Перед запуском парсеров cкопируйте категории проектов с помощью flr_categories'
    elif options.projects:
        print u'Удаление всех проектов'
        model.drop_projects()
        print u'Готово'
    else:
        parser.print_help()
    sys.exit()
