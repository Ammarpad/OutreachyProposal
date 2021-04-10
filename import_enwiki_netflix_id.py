#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

from time import sleep
from requests import ReadTimeout

import pywikibot
import get_statements2
import base_import_script

NETFLIX_ID_PROPERTY = 'P1874'

def import_netflix_ids():
    """
    Import multiple Netflix IDs ('P1874') from English Wikipedia
    to the Wikidata and add them to the respective data pages of
    the pages.
    This uses the pages in 'Category:Netflix_title_ID_not_in_Wikidata'
    """
    CATEGORY = 'Netflix title ID not in Wikidata'
    wiki = pywikibot.Site('en', 'wikipedia')

    data = base_import_script.get_all_pages(wiki, CATEGORY)
    pages = data['pages']
    
    all_ids = []
    no_data_item = []
    
    print('Beginning iterating through pages of "%s". There are %s pages.' %(data['title'], data['count']))
    
    for page in pages:
        title = page.title()
        try:
            result = get_netflix_id(wiki, title)
            # Skip if we couldn't extract the id
            # or if it already exists on the repo
            if not result or result['repo_value']
                continue
            all_ids.append([result['value'], page])
        except pywikibot.NoPage:
           print('Note: %s has no entity page' % title)
           no_data_item.append(title)
        except ReadTimeout:
            print('Caught ReadTimeout exception, retrying after 5 seconds...')
            sleep(5)
        
    print('Found %s potential Netflix ids to add' % len(all_ids))
    
    # Record pages with no data page (if any)
    base_import_script.record_pages_without_items(no_data_item, 'Netflix_no_data_item.txt')

    summary = u'Importing Netflix id from English Wikipedia'
    result = base_import_script.add_claims_to_item(wiki.data_repository(), all_ids, NETFLIX_ID_PROPERTY, summary)
    
    print('Finished! Added %s Netflix ids' % result['added'])

    if result['skipped']:
        print('%s ids were skipped because there was error during processing' % result['skipped'])

    return 1

def get_netflix_id(wiki, title):
    """
    This parses and article and attempt to get its Netflix identifier ('P1874')

    @param wiki: pywikibot.Site
    @param title: string title of the article
    @return: dictionary
    """
    regex = r'(https?:\/\/www\.netflix\.com\/(title|watch))\/(\d{6,8})'
 
    result = get_statements2.get_statement(wiki, title, regex, NETFLIX_ID_PROPERTY, source='text', ret=True)

    return result

if __name__ == '__main__':
    import_netflix_ids()