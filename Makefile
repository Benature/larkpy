version=0.2.2
project=larkpy

prepare:
	pip install -r requirements.txt

clean:
	rm -rf ./dist
	rm -rf ./build

uninstall:
	pip uninstall ${project} -y

install:
	pip install -U .

build:
	python -m build

all: uninstall clean build
	pip install -U dist/${project}-${version}-py3-none-any.whl

upload:
	twine upload dist/*