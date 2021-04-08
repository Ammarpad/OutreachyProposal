#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

import re
import requests
import pywikibot
import outreachyscript

def get_all_pages(cat_title):
    enwiki = pywikibot.Site('en', 'wikipedia')
    category = pywikibot.Category(enwiki, cat_title)
    count = category.categoryinfo['pages']
    title = category.title()
    pages = set(category.articles())

    result = {'pages': pages, 'count': count, 'title': title}

    return result

def add_claims_to_item(items, prop_id, summary, ):
    added = skipped = 0

    for i, page in items:
        try:
            outreachyscript.add_claim_to_item(repo, page.data_item(), prop_id, i, summary=summary)
            added += 1
        except pywikibot.Error as e:
            skipped += 1
            print('Error adding the claim: %s' % str(e) )  

    return {'added': added, 'skipped': skipped}
