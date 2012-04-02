#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import datetime

from elixir import session

import options
import model


if __name__ == '__main__':
    for project in model.Project.query.all():
        print '%8d: %s [%s]' % (project.id, project.name, project.url)
    #model.Category.query.count()
    sys.exit()
