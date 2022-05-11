#!/usr/bin/env python3
# vim: expandtab

import sys
import time
import math
import requests
from requests.cookies import RequestsCookieJar
from lxml import etree
from urllib import parse

def read_members():
    members = []
    with open('authors.txt', 'r') as fin:
        members = [ line.strip() for line in fin.readlines() ]
    return members

def single(process, author, req, fout):
    if sys.stdout.isatty():
        sys.stdout.write('\r\033[0K%s %s' % (process, author))
        sys.stdout.flush()
        return 0
    url = 'https://dblp.uni-trier.de/search?q=' + parse.quote(author)
    r = req.get(url)
    page = etree.HTML(r.text)
    journal_papers = page.xpath('//ul[@class="publ-list"]/li[@class="entry article toc"]')
    for journal_paper in journal_papers:
        title_list = journal_paper.xpath('cite/span[@class="title"]/text()')
        title = title_list and title_list[0] or '?'
        name_list = journal_paper.xpath('cite/a/span/span[@itemprop="name"]/text()')
        name = name_list and name_list[0] or '?'
        year_list = journal_paper.xpath('cite/span[@itemprop="datePublished"]/text()')
        year = year_list and year_list[0] or '?'
        venue = name + ' ' + year
        fout.write('%s,J,%s,%s,\n' % (author, venue, title))
        fout.flush()
    conf_papers = page.xpath('//ul[@class="publ-list"]/li[@class="entry inproceedings toc"]')
    for conf_paper in conf_papers:
        title_list = conf_paper.xpath('cite/span[@class="title"]/text()')
        title = title_list and title_list[0] or '?'
        name_list = conf_paper.xpath('cite/a/span/span[@itemprop="name"]/text()')
        name = name_list and name_list[0] or '?'
        year_list = conf_paper.xpath('cite/a/span[@itemprop="datePublished"]/text()')
        year = year_list and year_list[0] or '?'
        venue = name + ' ' + year
        fout.write('%s,C,%s,%s,\n' % (author, venue, title))
        fout.flush()

def main():
    req = requests.Session()
    fout = open('collection.csv', 'a')

    members = read_members()
    members_len = len(members)
    members_len_strlen = math.ceil(math.log(members_len + 1, 10))
    format_str = '%%%dd / %%d' % members_len_strlen
    cnt = 0
    for member in members:
        cnt += 1
        single(format_str % (cnt, members_len), member, req, fout)
        time.sleep(1)
    
    fout.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
