#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

import json
import requests
import pywikibot
import import_enwiki_soundcloud_id

from sclib import sync
from bs4 import BeautifulSoup
from pywikibot import pagegenerators
from urllib.error import (HTTPError, URLError)

CATEGORY = 'Category:SoundCloud ID different from Wikidata'
SOUNDCLOUD_BASE_URL = 'https://soundcloud.com/'

def check_soundcloud_ids_mismatch():
    """
    Check mismatch between SoundCloud IDs in Wikidata which are different
    from what is in the corresponing article in English Wikipedia.
    """
    wiki = pywikibot.Site('en', 'wikipedia')
    category = pywikibot.Category(wiki, CATEGORY)
    pages = pagegenerators.CategorizedPageGenerator(category)

    total_pages = 0
    processed = 0
    result = []

    for page in pages:
        total_pages += 1
        res = compare_soundcloud_ids(page, wiki)

        if res == True:
            # The IDs are the same, nothing to do. The category may contains cached entries
            print('The ID for "%s" are the same in both the article and Wikidata.' % page.title())
            processed += 1
            continue
        elif not res:
            print('Skipping %s. It has no SoundCloud ID' % page.title())
            processed += 1
            continue

        result.append([res, page.title()])

    for ids, title in result:
        # Now we have two IDs (one from article, another from repo).
        # Let us check their associated movie titles in the website
        repoId = ids['repoId']
        wikiId = ids['articleId']
        c_url, response_code1 = check_soundcloud_id(repoId)
        c_url2, response_code2 = check_soundcloud_id(wikiId)

        if c_url != '' and c_url == c_url2:
            # Both valid
            print('''Both SoundClouds IDs are valid for the title. %s''' % title)
            processed += 1
        elif response_code1 == 404 and response_code1 != response_code2:
            processed += 1
        elif response_code2 == 404 and response_code2 != response_code1:
            processed += 1
        else:
            pass

    print('Finished! Total pages: %s. Processed: %s' %(total_pages, processed))

def check_soundcloud_id(id):
    """
    Given a valid SoundCloud identifier, this function queries the website
    and get the canonical location of the page

    @param id: SoundCloud identifier.
    @return List[] canonical url of the title or empty string, and the response code
    """
    c_url = ''

    try:
       page = sync.get_page(SOUNDCLOUD_BASE_URL + str(id))
    except (HTTPError, URLError) as e:
       return c_url, e.code
    
    code = None
    if page:
        html = BeautifulSoup(page, 'html.parser')
        data = html.find('link', {'rel': 'canonical'})
        c_url = data['href']
        code = 200 # successful request

    return c_url, code

def compare_soundcloud_ids(page, wiki):
    """
    Extract the SoundCloud Id from the article and also extract it from the
    Wikidata Item. Then compare, if they're equal stop and return True as
    there's nothing to do. If they're not equal return their values for
    further processing.

    @param page: pywikibot.Page object
    @param wiki: pywikibot.Site object
    @return True if the IDs are equal, dict() if they are not;
        or None if we cannot extract the ID
    """

    result = import_enwiki_soundcloud_id.get_soundcloud_id(wiki, page.title())

    if result:
        articleId = result['value'] # extracted from article
        repoId = result['repo_value'] # extracted from repo

        if repoId == articleId:
            return True

        return {'repoId': repoId, 'articleId': articleId} # different

    return None

if __name__ == '__main__':
    check_soundcloud_ids_mismatch()
