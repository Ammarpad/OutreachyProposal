#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

import json
import requests
import pywikibot
import import_enwiki_netflix_id

from bs4 import BeautifulSoup
from pywikibot import pagegenerators

CATEGORY = 'Category:Netflix_title_ID_different_from_Wikidata'
NETFLIX_BASE_URL = 'https://www.netflix.com/title/'

def check_netflix_ids_mismatch():
    """
    Check mismatch between Netflix IDs in Wikidata which are different
    from what's in the corresponing article in English Wikipedia.
    """
    wiki = pywikibot.Site('en', 'wikipedia')
    category = pywikibot.Category(wiki, CATEGORY)
    pages = pagegenerators.CategorizedPageGenerator(category)

    total_pages = 0
    processed = 0

    result = []
    for page in pages:
        total_pages += 1
        res = compare_netflix_ids(page, wiki)

        if res == True:
            # The IDs are the same, nothing to do. The category may contains cached entries
            print('The ID for "%s" are the same in both the article and Wikidata.' % page.title())
            processed += 1
            continue
        elif not res:
            print('Skipping %s' % page.title())
            processed += 1
            continue

        result.append([res, page.title()])

    for ids, title in result:
        # Now we have two IDs (one from article, another from repo).
        # Let us check their associated movie titles in the website
        web_name1 = get_netflix_moviename(ids['repoId'])
        web_name2 = get_netflix_moviename(ids['articleId'])

        if web_name1 == web_name2:
            # Since the names are the same, then definitely both IDs are valid for the
            # title and visiting the base URL with either of the IDS will confirm this.
            print('''The movie {t} has two different Netflix IDs and are both correct.
                repoId: {rId}, articleId: {wId}. This can be confirmed by
                visiting {url}{rId} and {url}{wId} which will all resolved to
                the same page'''.format(t=title, rId=ids['repoId'], wId=ids['articleId'], url=NETFLIX_BASE_URL))
            processed += 1
        else:
            # At this stage, the IDs are still different and do not belong to the same title
            wiki_name = title.partition('(')[0].strip() # strip wiki disambiguation markers
            if web_name1 == wiki_name:
                print('The Wikidata netflix ID: %s is the correct one for the title %s:' %(ids['repoId'], title))
            elif web_name2 == wiki_name:
                print('The Article netflix ID: %s is the correct one for the title %s:' %(ids['articleId'], title))
            else:
                pass

    print("Total pages: %s. Processed: %s" %(total_pages, processed) )

def get_netflix_moviename(id):
    """
    Given a valid netflix identifier, this function queries the netflix
    website and attempt to extract the name from the JSON Linked Data in
    the page's html. (In absence of official API)
    This may help to resolve the Wikipedia-Wikidata data mismatches of
    https://en.wikipedia.org/wiki/Category:Netflix_title_ID_different_from_Wikidata

    @param id: Netflix Id
    @return string the movie name or empty string
    """
    page = requests.get('https://www.netflix.com/title/' + str(id))
    html = BeautifulSoup(page.content, 'html.parser')
    data = html.find('script', type='application/ld+json')

    name = ''

    if data:
        data = json.loads(data.string)
        name = data['name']

    return name

def compare_netflix_ids(page, wiki):
    """
    Extract the Netflix Id from the article and also extract it from the
    Wikidata Item. Then compare, if they're equal stop and return True as
    there's nothing to do. If they're not equal return their values for
    further processing.

    @param page: pywikibot.Page object
    @param wiki: pywikibot.Site object
    @return True if the IDs are equal, dict() if they are not;
        or None if we cannot extract the ID
    """

    result = import_enwiki_netflix_id.get_netflix_id(wiki, page.title())

    if result:
        articleId = result['value'] # extracted from article
        repoId = result['repo_value'] # extracted from repo

        if repoId == articleId:
            return True

        return {'repoId': repoId, 'articleId': articleId}

    return None


if __name__ == '__main__':
    check_netflix_ids_mismatch()
