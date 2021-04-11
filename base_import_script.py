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

    'pages': A list of pywikibot.Page objects
    'count': The total number of pages found
    'title': Title of the category for display

    @param wiki: Pywikibot.Site
    @param cat_title: Plain name of the category
    without the namespace prefix.
    @return dictionary with the keys mentioned above
    """
    category = pywikibot.Category(wiki, cat_title)
    count = category.categoryinfo['pages']
    title = category.title()
    pages = [*category.articles()]

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
    @param items: List of [id, page]; add id to the data item of page
    @param prop_id: The property ID
    @param summary: Optional edit summary to use
    @return dictionary with the keys mentioned above
    """
    added = skipped = 0

    # For adding reference
    enwiki_page = pywikibot.Page(wiki, 'English Wikipedia')
    enwiki_data_item = enwiki_page.data_item()
    ref_id = 'P143' # imported from Wikimedia project

    for i, page in items:
        page_item = page.data_item()
        qid = page_item.title()

        try:
            # Add the claim
            outreachyscript.add_claim_to_item(repo, page_item, prop_id, i, summary)
            # Also add a reference
            outreachyscript.add_reference(repo, qid, prop_id, ref_id, enwiki_data_item)
            added += 1
        except (pywikibot.Error, pywikibot.data.api.APIError) as e:
            skipped += 1
            print('Error: Adding claim to %s failed: %s' % (qid, str(e)))

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
