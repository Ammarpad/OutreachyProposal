#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

import re
import pywikibot
import get_statements2
import outreachyscript
import imp
imp.reload(outreachyscript)
def main():
    enwiki = pywikibot.Site('en', 'wikipedia')

    # Do all the work
    add_statements(enwiki)
    add_qualifiers(enwiki)
    add_references(enwiki)

def add_statements(enwiki):
    """
    Queries articles for potential statements to add to repo.
    If found, actually add them to the repo if they are not
    present there already.

    @param enwiki pywikibot.Site
    """
    statements_found = []
    # Commonly used regex
    netflix_id_regx = r'(https?:\/\/www\.netflix\.com\/(title|watch))\/(\d{6,8})'

    # Data is list of lists that we want work on. Each list is in the format:
    # title - Title of the article to search
    # regex - regex to search for looking for the statement
    # p_id - id of the property in the repo that's use for the value of the keyword
    # location - likely location of the fact (e.g: infobox or just entire text)
    data = [
        ['Jubilee_House', 'owners?', 'P127', 'infobox'], # QID
        ['Nigeria Prize for Literature', 'sponsors?', 'P859', 'infobox'], # QID
        ['Generation Revolution', netflix_id_regx, 'P1874', 'text'], # numeric id
        ['Ave Maryam', netflix_id_regx, 'P1874', 'text'], # numeric id
        ['Tatu (film)', netflix_id_regx, 'P1874', 'text'], # numeric id
        ['Fix Us', netflix_id_regx, 'P1874', 'text'], # numeric id
        ['Nigeria Prize for Literature', '(reward|prize money)', 'P2121', 'infobox'], # quantity
        ['Instituto Benjamin Constant', '(official)? website', 'P856', 'infobox'], # string (url)
        ['Ron Rocco', '(official)? website', 'P856', 'infobox'], # string (url)
        ['Thomas Witlam Atkinson', '\\[\\[File: (Alatau(.*))\\]\\]', 'P18', 'text'] # File
        ['Back to the Outback', '(released?|release date)', 'P577', 'infobox'], # date
        ['Ultimate Love (TV series)', '(released?|release date)', 'P577', 'infobox'], # date
        ['Lismore (Parliament of Ireland constituency)', '(abolished|disestablished)', 'P2043', 'infobox'], # date
    ]

    # Loop over the data and query each article for the statement
    for title, regex, p_id, location in data:
        result = get_statements2.get_statement(enwiki, title, regex, p_id, location, True)
        statements_found.append(result)

    print('Found %s potential statements to add' % len(statements_found))

    added = exists = 0
    # Iterate over the statements and actually push them to the repo
    # Report back the number of statements added and/or skipped
    for result in statements_found:
        if result and result['repo_value']:
            print('Repo already has the value for %s: %s' %(result['id'], result['repo_value']))
            exists += 1
            continue

        page = pywikibot.Page(enwiki, result['title'])
        res = add_statement(page, result['value'], result['id'])
        if res: added += 1

    if added: print('Done. Added %s statements' % added)
    if exists: print('%s statements were skipped' % exists)

    return 1

def add_statement(page, value, p_id):
    """
    Add a single statment to the data repo.

    @param page: pywikibot.Page
    @param value: string raw value of the statment culled from
        the article (may contains wikilinks, template braces, etc)
    @param p_id: string id of the property in the repo that's use
        for the items of the value found in the article
    """
    repo = page.site.data_repository()
    page_item = page.data_item().title()

    # Strip all internal and interwiki link
    # formattings because we attempt to search
    # for the local page. [[example]] -> example
    def strip_wikilinks(title):
        match = re.search(r'\[\[(.*?)\]\]', title)
        if match:
            title = match.group(1)

        match = re.search(r'..?:+(.*)', title)
        if match:
            title = match.group(1)

        match = re.match(r'\{\{(.*)\|(.*)\}\}', title)
        if match:
              title = match.group(2)

        return title

    if isinstance(value, str):
        title =  strip_wikilinks(value)
        value_page = pywikibot.Page(page.site, title)
    else:
       value_page = None

    # Follow redirect to get the relevant target
    if value_page:
        if value_page.isRedirectPage():
            value_page = value_page.getRedirectTarget()
            if value_page.exists():
                value = value_page.data_item().title()

    try:
        outreachyscript.add_claim_to_item(repo, page_item, p_id, value, summary=u"Adding claim")
        return 1
    except pywikibot.Error as e:
        print('Error adding the claim: %s' % str(e) )
        return 0

def add_qualifiers(enwiki):
    """
    Add qualifiers to an existing claim
    """
    repo = enwiki.data_repository()

    data = [
        # Add number of subscribers qualifier to claim P2002 of entity x
        ['Q100273559', 'P2002', 'P3744', pywikibot.WbQuantity(831000, site=repo)],
        ['Q3152360', 'P2002', 'P3744', pywikibot.WbQuantity(12600, site=repo)]
    ]

    added = skipped = 0
    for item_id, claim_id, prop_id, value in data:
        res = outreachyscript.add_qualifier(repo, item_id, claim_id, prop_id, value)
        if res:
            added += 1
        else:
            skipped += 1

    if added: print('Done. Added %s qualifiers' % added)
    if skipped: print('%s qualifiers were skipped' % skipped)

    return 1

def add_references(enwiki):
    """
    Add references to an existing claim
    """
    repo = enwiki.data_repository()
    ref_url = 'https://www.vanguardngr.com/2019/08/meet-dr-isa-ibrahim-pantami-minister-of-communications/'

    data = [
        # Add reference to claim 'P106' of entity Q42916213
        ['Q42916213', 'P106', 'P854', ref_url]
    ]

    added = skipped = 0
    for item_id, claim_id, prop_id, value in data:
        res = outreachyscript.add_reference(repo, item_id, claim_id, prop_id, value)
        if res:
            added += 1
        else:
            skipped += 1

    if added: print('Done. Added %s references' % added)
    if skipped: print('%s references were skipped' % skipped)

    return 1

if __name__ == '__main__':
    main()
