style:
	flake8

run_back_end:
	python manage.py runserver

run_front_end:
	parcel watch bundles-src/index.js -d bundles --public-url="./"