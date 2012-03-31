#! /usr/bin/env python
# -*- coding: utf-8 -*-

#import os
import os.path


log_dir = '/tmp/work/'
database_binding = 'mysql://root:654321@localhost/flgrab'
database_echo = False

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
