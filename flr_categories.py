#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser

from grab import Grab

import model


def get_categories():
    grab = Grab()
    grab.setup(url='http://www.free-lance.ru/freelancers/')

    print u'Запрос страницы'
    grab.request()

    print u'Извлечение категорий'
    categories = grab.xpath_list('//ul[@id="accordion"]/li[not(@class)]')

    for category in categories:
        subcategories = category.xpath('./ul[@class="element"]/li/span/a')
        subcategories = map(
                lambda a: a.text_content().encode('utf-8'),
                subcategories
            )

        yield (
                category.xpath('./a')[0].text_content().encode('utf-8'),
                subcategories
            )

    print u'Завершено'


def grab_all_categories():
    for category_name, subcategories in get_categories():
        print category_name, subcategories
        category_record = model.get_or_create(
                model.Category,
                name=category_name,
                parent=None,
                site=model.free_lance_ru
            )
        for subcategory_name in subcategories:
            model.get_or_create(
                    model.Category,
                    name=subcategory_name,
                    parent=category_record,
                    site=model.free_lance_ru
                )


def print_categories(with_subcategories=True, enumerating=True):
    def number_prefix(*arg):
        if not arg:
            return None
        post = number_prefix(*arg[1:])
        return '%d.%s' % (arg[0], post if post else '')

    def get_categories(parent=None):
        categories = model.Category.query
        categories = categories.filter_by(parent=parent)
        categories = categories.order_by(model.Category.name)
        return categories.all()

    print u'Общее количество категорий: %d' % (model.Category.query.count())
    print u'Категории:'

    for index, category in enumerate(get_categories()):
        print '%s %s' % (
                number_prefix(index+1) if enumerating else '',
                category.name
            )
        if not with_subcategories:
            continue
        subcategories = get_categories(parent=category)
        for subindex, subcategory in enumerate(subcategories):
            if not enumerating:
                prefix = ''
            else:
                prefix = number_prefix(index + 1, subindex + 1)
            print '  %s %s' % (
                    prefix,
                    subcategory.name
                )


def print_statistics():
    total = model.Category.query.count()
    parents = model.Category.query.filter_by(parent=None).count()

    print 'Категорий: %d\n Корневых: %d\n Дочерних: %d' % (
            total,
            parents,
            total - parents
        )


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
            '-g',
            '--grab',
            action="store_true",
            dest="grab",
            help=u'произвести парсинг сайта для извлечения категорий'
        )
    parser.add_option(
            '-p',
            '--print',
            action="store_true",
            dest="output",
            help=u'показать список всех категорий'
        )
    parser.add_option(
            '-n',
            '--enumerate',
            action="store_true",
            dest="enumerate",
            help=u'показывать порядковые номера категорий'
        )
    parser.add_option(
            '-s',
            '--statistics',
            action="store_true",
            dest="statistics",
            help=u'показать статистику'
        )
    options, args = parser.parse_args()
    if options.grab:
        grab_all_categories()
    elif options.output:
        print_categories(enumerating=options.enumerate)
    elif options.statistics:
        print_statistics()
    else:
        parser.print_help()
    sys.exit()
