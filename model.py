#! /usr/bin/env python
# -*- coding: utf-8 -*-

from elixir import *
from sqlalchemy.dialects.mysql import LONGTEXT

import options


class Site(Entity):
    url = Field(String(256), unique=True)
    icon = Field(String(256), unique=True)

    projects = OneToMany('Project')
    categories = OneToMany('Category')

    def __init__(self, **kwars):
        for key, value in kwars.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<Site "%s">' % (self.url)


class Category(Entity):
    name = Field(String(256))

    parent = ManyToOne('Category')
    childs = OneToMany('Category')

    site = ManyToOne('Site')

    projects = OneToMany('Project')

    def __init__(self, **kwars):
        for key, value in kwars.items():
            setattr(self, key, value)

    def path(self):
        return [self.name] + (self.parent.path() if self.parent else [])

    def __repr__(self):
        return '<Category %s>' % ('/'.join(self.path()))


class Project(Entity):
    url = Field(String(256))
    name = Field(String(256))
    description = Field(LONGTEXT)
    date = Field(DateTime)

    category = ManyToOne('Category')

    site = ManyToOne('Site')

    def __init__(self, **kwars):
        for key, value in kwars.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<Project %s>' % (self.name)


def get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        return model(**kwargs)


metadata.bind = options.database_binding
metadata.bind.echo = options.database_echo

setup_all()
create_all()


free_lance_ru = get_or_create(Site, url='http://free-lance.ru/')
weblancer_net = get_or_create(Site, url='http://weblancer.net/')
