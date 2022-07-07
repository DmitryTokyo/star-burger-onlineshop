#!/bin/bash

make run_front_end &
venv/bin/python3 manage.py runserver

wait