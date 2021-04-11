#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

import pywikibot
import re

def search_terms_for_qids(lang):
    wiki = pywikibot.Site(lang, 'wikipedia')
    wikidata = wiki.data_repository()

    # Pages from work in Task 1
    page = pywikibot.Page(wikidata, u'User:Ammarpad/Outreachy 1')

    # Find all page titles linking back to Wikipedia in 'lang'
    titles = re.findall(r'\[\[:%s:(.*?)\]\]' % lang, page.text)

    langs = {'fr': 'FRENCH', 'en': 'ENGLISH', 'ar': 'ARABIC'}

    print('RUNNING THE SCRIPT FOR %s WIKIPEDIA (%s pages)' %(langs[lang], len(titles)))

    found = 0
    for t in titles:
        # Work around bidirectionality problem for strings in parentetheses
        if lang == 'ar':
            print('...%s Searching for' % t)
        else:
            print('Searching for %s...' % t)

        res = [*wikidata.search_entities(t, lang, None, **{'type': 'item'})]
        print('Found %s matching results.' % len(res))

        for i in res:
            try:
                page = pywikibot.Page(wiki, i['match']['text'])
                if page.isRedirectPage():
                    page = page.getRedirectTarget()
                qid = page.data_item().title()

            except pywikibot.NoPage:
                print('Coundn\'t find the QID for %s' % t)
                continue

            if i['id'] == qid:
                print('Found the page\'s QID: {title} -> {qid}.'.format(title=t, qid=qid))
                found += 1
                break

            print('Coundn\'t find the QID for %s' % t)

    print('Finished! Found %s QIDs in total' % found)

if __name__ == '__main__':
    # Run for French, Arabic and English pages
    search_terms_for_qids('fr')
    search_terms_for_qids('ar')
    search_terms_for_qids('en')
