#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

import re
from time import sleep
import requests
import pywikibot
import get_statements2
import outreachyscript

def import_soundcloud_ids():
    cat_title = 'SoundCloud ID not in Wikidata'
    enwiki = pywikibot.Site('en', 'wikipedia')
    category = pywikibot.Category(enwiki, cat_title)
    page_count = category.categoryinfo['pages']
    pages = set(category.articles())
    
    all_ids = []
    no_data_item = []
    
    print('Beginning iterating through pages of "%s". There are %s pages.' %(category.title(), page_count))
    
    for page in pages:
        try:
            result = get_soundcloud_id(enwiki, page.title())
            all_ids.append([result, page])
        except pywikibot.NoPage:
           print('%s has no entity page' % page.title())
           no_data_item.append(page.title())
        except requests.ReadTimeout:
            print('Caught ReadTimeout exception, retrying after 5 seconds...')
            sleep(5)
        
    print('Found %s potential SoundClound ids to add' % len(all_ids))
    
    if len(no_data_item):
        with open('no_data_item.txt', mode='w', encoding='utf-8') as file:
            for i in no_data_item:
                file.write(i + '\n')
        print('%s pages however don\'t have wikidata item. ' \
            'Their titles can be found in %s' % len(no_data_item, os.path.abspath('no_data_item.txt')))
    
    del no_data_item

    added = skipped = 0
    for s_id, page in all_ids:
        try:
            summary = u'Importing SoundClound id from English Wikipedia'
            outreachyscript.add_claim_to_item(repo, page.data_item(), 'P3040', s_id, summary=summary)
            added += 1
        except pywikibot.Error as e:
            skipped += 1
            print('Error adding the claim: %s' % str(e) )   

    print('Finished! Added %s SoundClound ids' % added)

    if skipped:
        print('%s ids were skipped because there was error during processing' % skipped)


def get_soundcloud_id(wiki, title):
    regex = r'(https?:\/\/(wwww\.)?soundcloud\.com\/(\w*))'
 
    s_id = get_statements2.get_statement(wiki, title, regex, 'P3040', source='text', ret=True)

    return s_id

if __name__ == '__main__':
    import_soundcloud_ids()