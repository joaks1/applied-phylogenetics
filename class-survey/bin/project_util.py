#! /usr/bin/env python

import os
import sys

BIN_DIR = os.path.abspath(os.path.dirname(__file__))
SURVEY_DIR = os.path.abspath(os.path.dirname(BIN_DIR))
DATA_DIR = os.path.abspath(os.path.join(SURVEY_DIR, 'data'))
PLOT_DIR =  os.path.abspath(os.path.join(SURVEY_DIR, 'plots'))
if not os.path.exists(PLOT_DIR):
    os.mkdir(PLOT_DIR)

def main():
    sys.stdout.write("%s" % SURVEY_DIR)

if __name__ == '__main__':
    main()

