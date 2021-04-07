#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

import pywikibot
import re

def get_statement(wiki, title, key, pid, source=None, ret=False):
    """
    Convenience function to access the two key functions that do the heavy work

    @param wiki: Wiki site pywikibot.Site
    @param title: The article title
    @param key: The key to search for (a simple string or subregex)
    @param pid: The property id
    @param source: likely location to find the fact (e.g: infobox or just entire text)
    @param ret: Return the result instead of printing
    """
    if source == 'infobox':
        result = get_statement_from_infobox(wiki, title, key, pid, ret)
    elif source == 'text':
        result = get_statement_from_text(wiki, title, key, pid, ret)
    else:
        result = None

    if ret:
        return result
    else:
        return 0

def get_statement_from_infobox(wiki, title, key, pid, ret=False):
    """
    This searches an article and attempts to get where a certain
    statement is used. It also then checks the Item page in the
    repo to let us see whether the statement we got is correct or
    is at least in sync with what is currently in the repo. Both
    values got are then printed out.

    @param wiki: Wiki site pywikibot.Site
    @param title: The article title
    @param key: The key to search for (a simple string or subregex)
    @param pid: The property id
    @param ret: Return the result instead of printing
    """
    page = pywikibot.Page(wiki, title)

    # Search the article text and look for the pattern ( key = value )
    # This is the pattern used in most infoboxes of Wikipedia
    # articles where there's a key-value pair of property and value. Both
    # the key and the value are case-insensitive.
    result = re.findall(r"%s *[=] *(.*)" % key, page.text, re.IGNORECASE)
    count = len(result)

    if count:
        # Now attempt to extract the value from the result
        # and also get the corresponding claim from the repo
        def loop_through_result(result, count, key):
            value = None
            tries = count
            i = 0
            while True:
                value = result[i]
                i += 1
                tries -= 1

                # Repeat if we are at the key index still
                if type(value) == str and value in key:
                    continue

                if value or not tries:
                    break

            return value

        value = loop_through_result(result, count, key)

        # Loop through the value again if we are still not done
        if type(value) == tuple:
            value = loop_through_result(value, len(value), key)

        if not value:
            print('There was a problem. The statement cannot be found')
            return 0

        value = value.strip()
        p = pywikibot.PropertyPage(wiki.data_repository(), pid)
        prop = p.labels['en'] + f' ({pid})'

        # More work needed for English Wikipedia {{coordinate}} template
        # If value is coordinate now, we need to extract the real value
        # from the the sorrounding template
        needs_extraction = "{{coord|" in value or "{{Coord|" in value
        if needs_extraction:
            value = re.findall(r'-?\d+\.?\d*', value)

        result = {}
        # First result from manual search
        if not ret:
            print(f'Result: {prop} = {value}')
        else:
            result['id'] = pid
            result['title'] = title
            result['value'] = value
            result['repo_value'] = None

        item = page.data_item()
        item_dict = item.get()

        # Check the repo in case the claim already exists
        value2 = check_repo(page.data_item(), pid)

        if not ret:
            print(f'The {prop} from parsing the article is: {value}'
                + f' and the  {prop} from the item page is: {value2}\n')
            return 1
        else:
            result['repo_value'] = value2
        return result
    else:
        print('There was a problem. The statement cannot be found 0')
        return 0

def get_statement_from_text(wiki, title, regex, pid, ret=False):
    """
    Variant of get_statement_from_infobox() which uses the expanded page
    text. Slower, but can find facts hidden in template and other wikitext
    nesting logic.
    Parameters same as get_statement_from_infobox()
    """
    page = pywikibot.Page(wiki, title)

    if page.isRedirectPage():
        page = page.getRedirectTarget()

    page_source = page.expand_text(True)

    result = re.search(r'%s' % regex, page_source, re.I)
    value = {'repo_value' : None}

    repo_check = check_repo(page.data_item(), pid)
    if repo_check:
        value['repo_value'] = repo_check

    if result:
        val = result.group(result.lastindex)
        if ret:
            value['id'] = pid
            value['title'] = title
            value['value'] = val
            return value
        else:
            print('Found: %s' % val)
            return 1

    if not ret: print('No result was found')
    return None

def check_repo(item, p_id):
    """
    Checks the repo to find whether a particular claim already exists
    on the target item.
    @param item, the item
    @param p_id: the property id
    """
    item_dict = item.get()
    value = None

    for claim in item_dict['claims'].get(p_id, None) or {}:
        claim_target = claim.getTarget()
        if isinstance(claim_target, pywikibot.WbQuantity):
           value = claim_target.amount
        elif isinstance(claim_target, pywikibot.Coordinate):
            value = str(claim_target.lat) + ', ' + str(claim_target.lon)
        elif isinstance(claim_target, pywikibot.WbTime):
            value = claim_target.toTimestamp()
        elif isinstance(claim_target, pywikibot.FilePage):
            value = claim_target.title()
        elif isinstance(claim_target, pywikibot.ItemPage):
            claim_dict = claim_target.get()
            value = claim_dict['labels']['en']
        else:
            value = claim_target

        return value


"""RUN OUTPUT"""
if __name__ == '__main__':
    enwiki = pywikibot.Site('en', 'wikipedia')

    # Radcliffe Observatory, owner (P127)
    get_statement_from_infobox(enwiki, 'Radcliffe Observatory', 'owner', 'P127')
    # Result: owned by (P127) = [[Green Templeton College, Oxford|Green Templeton College]]
    # The owned by (P127) from parsing the article is: [[Green Templeton College, Oxford|Green Templeton College]] and the  owned by (P127) from the item page is: Green Templeton College

    # Radcliffe Observatory, architecture style (P149)
    get_statement_from_infobox(enwiki, 'Radcliffe Observatory', 'architectural_style', 'P149')
    # Result: architectural style (P149) = [[Neoclassical architecture|Neoclassical]]
    # The architectural style (P149) from parsing the article is: [[Neoclassical architecture|Neoclassical]] and the  architectural style (P149) from the item page is: Neoclassical architecture

    # Radcliffe Observatory, image (P18)
    get_statement_from_infobox(enwiki, 'Radcliffe Observatory', 'image', 'P18')
    # Result: image (P18) = Oxford ClarendonObservatory.jpg
    # The image (P18) from parsing the article is: Oxford ClarendonObservatory.jpg and the  image (P18) from the item page is: File:Green Templeton College.jpg

    # Radcliffe Observatory, architect (P84)
    get_statement_from_infobox(enwiki, 'Radcliffe Observatory', 'architect', 'P84')
    # Result: architect (P84) = [[Henry Keene]] and [[James Wyatt]]
    # The architect (P84) from parsing the article is: [[Henry Keene]] and [[James Wyatt]] and the  architect (P84) from the item page is: Henry Keene

    # Radcliffe Observatory, designation (P1435)
    get_statement_from_infobox(enwiki, 'Radcliffe Observatory', 'designations?', 'P1435')
    # Result: heritage designation (P1435) = [[Listed building#Categories of listed building|Listed Grade I]]
    # The heritage designation (P1435) from parsing the article is: [[Listed building#Categories of listed building|Listed Grade I]] and the  heritage designation (P1435) from the item page is: Grade I listed building

    # Radcliffe Observatory, location (P131)
    get_statement_from_infobox(enwiki, 'Radcliffe Observatory', '(location|administrative_region)', 'P131')
    # Result: located in the administrative territorial entity (P131) = [[Woodstock Road (Oxford)|Woodstock Road]], [[Oxford]]
    # The located in the administrative territorial entity (P131) from parsing the article is: [[Woodstock Road (Oxford)|Woodstock Road]], [[Oxford]] and the  located in the administrative territorial entity (P131) from the item page is: Oxford

    # Radcliffe Observatory, coordinates (P625)
    get_statement_from_infobox(enwiki, 'Radcliffe Observatory', 'coordinates', 'P625')
    # Result: coordinate location (P625) = 51.7608, -1.2639
    # The coordinate location (P625) from parsing the article is: 51.7608, -1.2639 and the  coordinate location (P625) from the item page is: 51.7608, -1.2639

    # Washington Agreement (1994), language (P407)
    get_statement_from_infobox(enwiki, 'Washington Agreement (1994)', 'language[s]?', 'P407')
    # Result: language of work or name (P407) = [[Bosnian language|Bosnian]] and [[Croatian language|Croatian]]
    # The language of work or name (P407) from parsing the article is: [[Bosnian language|Bosnian]] and [[Croatian language|Croatian]] and the  language of work or name (P407) from the item page is: Bosnian

    # King's Observatory, architect (P84)
    get_statement_from_infobox(enwiki, "King's Observatory", 'architect', 'P84')
    # Result: architect (P84) = [[Sir William Chambers]]
    # The architect (P84) from parsing the article is: [[Sir William Chambers]] and the  architect (P84) from the item page is: William Chambers

    # Sophia (robot), manufacturer (P176)
    get_statement_from_infobox(enwiki, 'Sophia (robot)', '(manufacturer|maker|producer)', 'P176')
    # Result: manufacturer (P176) = Hanson Robotics logo.png
    # The manufacturer (P176) from parsing the article is: Hanson Robotics logo.png and the  manufacturer (P176) from the item page is: Hanson Robotics Limited

    # Moshood Abiola National Stadium, seating_capacity, (P1083)
    get_statement_from_infobox(enwiki, 'Moshood Abiola National Stadium', 'seating_capacity', 'P1083')
    # Result: maximum capacity (P1083) = 60,491 (football)
    # The maximum capacity (P1083) from parsing the article is: 60,491 (football) and the  maximum capacity (P1083) from the item page is: 60491

    # Roberts International Airport, service area (P931)
    get_statement_from_infobox(enwiki, 'Roberts International Airport', '[(.*)]?serve[s|d|]?', 'P931')
    # Result: place served by transport hub (P931) = [[Monrovia]], Liberia
    # The place served by transport hub (P931) from parsing the article is: [[Monrovia]], Liberia and the  place served by transport hub (P931) from the item page is: Monrovia

    # British Phycological Society, inception (P571)
    get_statement_from_infobox(enwiki, 'British Phycological Society', '(formation|inception|started|founded)', 'P571')
    # Result: inception (P571) = 1952
    # The inception (P571) from parsing the article is: 1952 and the  inception (P571) from the item page is: 1952-07-01T00:00:00Z


    frwiki = pywikibot.Site('fr', 'wikipedia')

    # Dark Horse Presents, publisher (P123)
    get_statement_from_infobox(frwiki, 'Dark Horse Presents', 'éditeur', 'P123')
    # Result: publisher (P123) = [[Dark Horse Comics]]
    # The publisher (P123) from parsing the article is: [[Dark Horse Comics]] and the  publisher (P123) from the item page is: Dark Horse Comics

    # Fred Haise, country of citizenship (P27)
    get_statement_from_infobox(frwiki, 'Fred Haise', 'nationalit[é|e]', 'P27')
    # Result: country of citizenship (P27) = [[États-Unis|américain]]
    # The country of citizenship (P27) from parsing the article is: [[États-Unis|américain]] and the  country of citizenship (P27) from the item page is: United States of America

    # Valeurs familiales, author (P50)
    get_statement_from_infobox(frwiki, 'Valeurs familiales', 'auteur', 'P50')
    # Result: author (P50) = Frank Miller
    # The author (P50) from parsing the article is: Frank Miller and the  author (P50) from the item page is: Frank Miller

    # Jennifer Sidey, occupation (P106)
    get_statement_from_infobox(frwiki, 'Jennifer Sidey', '[occupation] (actuelle|précédente)', 'P106')
    # Result: occupation (P106) = [[astronaute]]
    # The occupation (P106) from parsing the article is: [[astronaute]] and the  occupation (P106) from the item page is: astronaut
