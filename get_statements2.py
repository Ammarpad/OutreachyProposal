#!/usr/bin/env python3

import pywikibot
import re

def get_statement_from_infobox(wiki, title, key, pid):
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
            value = value[0] + ', ' + value[1]

        # First result from manual search
        print(f'Result: {prop} = {value}')

        item = page.data_item()
        item_dict = item.get()

        for claim in item_dict['claims'][pid]:
            claim_target = claim.getTarget()
            if isinstance(claim_target, pywikibot.WbQuantity):
               value2 = claim_target.amount
            elif isinstance(claim_target, pywikibot.Coordinate):
                value2 = str(claim_target.lat) + ', ' + str(claim_target.lon)
            elif isinstance(claim_target, pywikibot.WbTime):
                value2 = claim_target.toTimestamp()
            elif isinstance(claim_target, pywikibot.FilePage):
                value2 = claim_target.title()
            else:
                claim_dict = claim_target.get()
                value2 = claim_dict['labels']['en']

            # Second result from repo
            print(f'The {prop} from parsing the article is: {value}'
                + f' and the  {prop} from the item page is: {value2}\n')
            return 1
    else:
        print('There was a problem. The statement cannot be found 0')
        return 0

"""RUN OUTPUT"""
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
