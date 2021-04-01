#!/usr/bin/env python3

import pywikibot
import re

def get_statement_from_article():
    """
    This parses an article and attempts to get where a certain
    statement is used (In this case author statement).
    It also then checks the Item page in the repo to let us see
    whether the statement we got is correct or is at least in sync
    with what is currently in the repo. Both values got are then
    printed out.
    """

    # Connect to French Wikipedia
    frwiki = pywikibot.Site('fr', 'wikipedia')
    frwiki_repo = frwiki.data_repository()

    # The title we use (https://fr.wikipedia.org/wiki/Valeurs_familiales)
    title = 'Valeurs familiales'

    # Get its page object
    page = pywikibot.Page(frwiki, title)

    # Search the article text and look for the pattern ( Auteur = value )
    # This is the pattern used in most infoboxes of Wikipedia articles where there's
    # a key-value pair of property and value. 'Auteur' means 'Author' in French and
    # we don't care about the case of the string so we passed the re.IGNORECASE flag
    # 'value' is what we are eventually looking for and it will be the author name.
    result = re.search(r"Auteur *[^\w ] *(.*)", page.text, re.IGNORECASE)

    if result:
        # Now extract only the value from the result
        # (which is the author name) and on the right hand side of the equal sign
        result = result.group().split('=')
        author_name = result[1]

        # Print it
        print('Result: author (P50) = ' + author_name )

        # We can also attempt to load the real Item page and see whether we got
        # it correct. QID of our relevant page 'Valeurs familiales' is Q1191530
        # Author property is P50
        item_id = 'Q1191530'
        item = pywikibot.ItemPage(frwiki_repo, item_id)
        item_dict = item.get()

        for claim in item_dict['claims']['P50']:
            author_prop_item_dict = claim.getTarget().get()
            author_name2 = author_prop_item_dict['labels']['fr']

            print('The Author name from parsing the article is: ' + author_name
                + ' and the Author name from the item page is: ' + author_name2)
            return 1
    else:
        print('There was a problem. The statement cannot be found')
        return 0


"""Sample run output"""
# Python 3.8.0 (v3.8.0:fa919fdf25, Oct 14 2019, 10:23:27)
# [Clang 6.0 (clang-600.0.57)] on darwin
# Type "help", "copyright", "credits" or "license" for more information.
# >>> import get_statements
# >>> get_statements.get_statement_from_article()
# Result: author (P50) =  Frank Miller
# The Author name from parsing the article is:  Frank Miller and the Author name from the item page is: Frank Miller
# 1
