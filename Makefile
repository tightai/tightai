SRC = $(wildcard ./*.ipynb)

all: nbdev_template docs

nbdev_template: $(SRC)
	nbdev_build_lib
	touch nbdev_template

docs_serve: docs
	cd docs && bundle exec jekyll serve

docs: $(SRC)
	nbdev_build_docs
	touch docs

test:
	nbdev_test_nbs

release: pypi
	nbdev_bump_version

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

cli: clean
	nbdev_build_lib 
	python setup.py sdist bdist_wheel
	cp -R dist/ ~/tight/my-tight-apps/local_dev/whl

clean:
	rm -rf dist