===========
IKEA goods
===========

Collecting all goods from IKEA

- using Scrapy
- output in csv
- defining yellow price

Run
==========

::

$ cd ikeagoods/scrapyparser
$ crawl goods -o output.csv -t csv

Todo
=========

1. add timestamp to parser's name `output.csv` file
2. fix is_yellow price checker
3. add datetime column to table
4. some of goods missed - for example: https://www.ikea.com/ru/ru/cat/aksessuary-dlya-hraneniya-st007/
5. collect all categories info
