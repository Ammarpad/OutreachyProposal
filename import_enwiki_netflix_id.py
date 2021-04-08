#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

from time import sleep
from requests import ReadTimeout

import pywikibot
import get_statements2
import outreachyscript
import base_import_script

NETFLIX_ID_PROPERTY = 'P3040'

def import_netflix_ids():
    CATEGORY = 'Netflix title ID not in Wikidata'
    
    data = base_import_script.get_all_pages(CATEGORY)

    pages = data['pages']
    
    all_ids = []
    no_data_item = []
    
    print('Beginning iterating through pages of "%s". There are %s pages.' %(data['title'], data['count']))
    
    for page in pages:
        try:
            result = get_netflix_id(enwiki, page.title())
            all_ids.append([result, page])
        except pywikibot.NoPage:
           print('Note: %s has no entity page' % page.title())
           no_data_item.append(page.title())
        except ReadTimeout:
            print('Caught ReadTimeout exception, retrying after 5 seconds...')
            sleep(5)
        
    print('Found %s potential Netflix ids to add' % len(all_ids))
    
    if len(no_data_item):
        with open('no_data_item.txt', mode='w', encoding='utf-8') as file:
            for i in no_data_item:
                file.write(i + '\n')
        print('%s pages however don\'t have wikidata item. ' \
            'Their titles can be found in %s' % (len(no_data_item), os.path.abspath('Netflix_no_data_item.txt')))
    
    del no_data_item

    summary = u'Importing Netflix id from English Wikipedia'
    result = base_import_script.add_claims_to_item(all_ids, NETFLIX_ID_PROPERTY, summary)
    
    print('Finished! Added %s Netflix ids' % result['added'])

    if result['skipped']:
        print('%s ids were skipped because there was error during processing' % result['skipped'])

    return 1

def get_netflix_id(wiki, title):
    regex = r'(https?:\/\/www\.netflix\.com\/(title|watch))\/(\d{6,8})'
 
    result = get_statements2.get_statement(wiki, title, regex, NETFLIX_ID_PROPERTY, source='text', ret=True)

    return result['value']

if __name__ == '__main__':
    import_netflix_ids()