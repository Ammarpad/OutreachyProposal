#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

import pywikibot
import outreachyscript

def get_all_pages(wiki, cat_title):
    """
    Retrieve all pages from a given category and
    return a dictionary with the following keys:

    'pages': A set of pywikibot.Page objects
    'count': The total number of pages found
    'title': Title of the category for display

    @param wiki: Pywikibot.Site
    @param cat_title: Plain name of the category
    without the namespace prefix.
    @return dict
    """
    category = pywikibot.Category(wiki, cat_title)
    count = category.categoryinfo['pages']
    title = category.title()
    pages = set(category.articles())

    result = {'pages': pages, 'count': count, 'title': title}

    return result

def add_claims_to_item(repo, items, prop_id, summary=''):
    """
    Push claims to the data repository, handle error
    and return a dictionary with the following keys:

    'added': The number of claims successfuly published
    'skipped': The number of claims which could not be saved
    due to duplication or other error (if any)

    @param repo: DataSite object
    @param items: List of the claims to add
    @param prop_id: The property ID
    @param summary: Optional edit summary to use
    @return dict
    """
    added = skipped = 0

    for i, page in items:
        try:
            outreachyscript.add_claim_to_item(repo, page.data_item(), prop_id, i, summary=summary)
            added += 1
        except pywikibot.Error as e:
            skipped += 1
            print('Error adding the claim: %s' % str(e) )  

    return {'added': added, 'skipped': skipped}


def record_pages_without_items(titles, file_name):
    """
    Write list of titles to the file_name.
    Does nothing if the titles list is empty

    @param titles: List of titles to record
    @param file_name: Name of file to write to
    """
    if len(titles):
        with open(file_name, mode='w', encoding='utf-8') as file:
            for t in titles:
                file.write(t + '\n')
        print('%s pages however don\'t have wikidata item. ' \
            'Their titles can be found in %s' % (len(titles), os.path.abspath(file_name)))
