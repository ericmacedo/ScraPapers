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
	- [ ] PDF transcription
- [x] Springer
	- Content and Metadata parsed
	- [ ] PDF transcription
- [x] Wiley
	- Content and Metadata parsed
	- Wiley's has several access limitations, it is very possible that the requests fail after a few tries
	- [ ] PDF transcription

## Output format

After scraping and processing your corpus, in the newly created folder `output` you can find:
- `corpus/` - contains the corpus as JSON files
	- `{doc_id}.json`:
	```json
	{
		"id": "md5 calculated from from the DOI number",
		"doi": "prefix/suffix",
		"url": "https://github.com/ericmacedo/ScraPapers",
		"title": "Some awesome title",
		"authors": [
			"Eric Macedo Cabral", "Some awesome author" // plain name format
		],
		"content": "Some awesome content",
		"abstract": "Some awesome abstract",
		"citations": 0,
		"source": "Some awesome source",
		"date": "yyyy-mm-dd", // ISO-8601
		"references": [
			"Awesome reference 1", "Awesome reference 2" // no format in particular
		]
	}
	```
	- `vocab.tsv` - the corpus' ngrams (1-3 by default) sorted alphabetically and their count

---
## To do

- [ ] Proxy configuration
- [ ] Command Line Interface (CLI)
	- [x] Get DOI list from txt file
	- [x] Get DOI list from tabular file
- [ ] TK user interface
- [ ] Docker infrastructure
