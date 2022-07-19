# ScraPapers

[![Python](https://img.shields.io/static/v1?label=Python&message=3.10.5&color=yellow)](https://www.python.org/downloads/release/python-369/)
[![PyPi](https://img.shields.io/static/v1?label=PyPi&message=22.1.2&color=blue)](https://pypi.org/project/pip/21.2.4/)

## Dependencies

- Firefox must be installed in the operating system
- Mozilla's [GeckoDriver (v0.31.0)](https://github.com/mozilla/geckodriver/releases/tag/v0.31.0) is already included in the repository as `./webdriver/`
	- `geckodriver.lixux`: for Linux
	- `geckodriver.osx`: for MacOS
	- `geckodriver.exe`: for Windows

## Available Scrapers

- [x] BioMed Central
	- Content and metadata parsed
- [x] IEEE Xplorer
	- Metadata parsed
	- Content parsed when content in HTML page
	- PDF transcription when only PDF available
- [x] ACM Digital Library
	- Metadata parsed
	- PDF transcription
- [x] Elsevier
	- Content and metadata parsed
- [x] Springer
	- Content and Metadata parsed
- [x] Wiley
	- Content and Metadata parsed
	- Wiley's has several access limitations, it is very possible that the requests fail after a few tries

## To do

- [ ] Proxy configuration
