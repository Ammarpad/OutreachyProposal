#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

from time import sleep
from requests import ReadTimeout

import pywikibot
import get_statements2
import base_import_script

SOUNDCLOUD_ID_PROPERTY = 'P3040'

def import_soundcloud_ids():
    """
    Import multiple SoundCloud IDs ('P3040') from English Wikipedia
    to the Wikidata and add them to the respective data pages of
    the pages.
    This uses the pages in 'Category:SoundCloud ID not in Wikidata'
    """
    CATEGORY = 'SoundCloud ID not in Wikidata'
    wiki = pywikibot.Site('en', 'wikipedia')

    data = base_import_script.get_all_pages(wiki, CATEGORY)
    pages = data['pages']
    
    all_ids = []
    no_data_item = []
    
    print('Beginning iterating through pages of "%s". There are %s pages.' %(data['title'], data['count']))
    
    for page in pages:
        title = page.title()
        try:
            res = get_soundcloud_id(wiki, title)
            # Skip if we couldn't extract the id
            # or if it already exists on the repo
            if not res or res['repo_value']:
                print('Note: Skipping %s because there\'s no ID or it already exists in repo' % title)
                continue
            all_ids.append([res['value'], page])
        except pywikibot.NoPage:
           print('Note: %s has no entity page' % title)
           no_data_item.append(title)
        except ReadTimeout:
            print('Caught ReadTimeout exception; retrying after 5 seconds...')
            sleep(5)

        if len(all_ids) == 20: # Do this in batches of 20
            print('Found 20 IDs to use for first batch run.')
            break
        
    print('Found %s potential SoundClound ids to add' % len(all_ids))
    
    # Record pages with no data page (if any)
    base_import_script.record_pages_without_items(no_data_item, 'Soundcloud_no_data_item.txt')

    summary = u'Importing SoundClound id from English Wikipedia'
    result = base_import_script.add_claims_to_item(wiki.data_repository(), all_ids, SOUNDCLOUD_ID_PROPERTY, summary)
    
    print('Finished! Added %s SoundClound ids' % result['added'])

    if result['skipped']:
        print('%s ids were skipped because there was error during processing' % result['skipped'])

    return 1

def get_soundcloud_id(wiki, title):
    """
    This parses an article and attempt to get its SoundCloud identifier ('P3040')

    @param wiki: pywikibot.Site
    @param title: string title of the article
    @return: dictionary or None
    """
    regex = r'(https?:\/\/(wwww\.)?soundcloud\.com\/(\w*))'
 
    result = get_statements2.get_statement(wiki, title, regex, SOUNDCLOUD_ID_PROPERTY, source='text', ret=True)

    return result

if __name__ == '__main__':
    import_soundcloud_ids()