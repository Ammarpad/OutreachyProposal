#!/usr/bin/env python3

import os
import sys
sys.path.append(os.environ['PYWIKIBOT_DIR'])

import pywikibot

def print_outreachy_page(site, title):
    """This loads and prints the text of a page"""
    page = pywikibot.Page(site, title)
    text = page.get()
    print(text)

def append_hello(site, title):
    """
    This tries to append to a page.
    It does not create new page if the page does not exist
    """
    page = pywikibot.Page(site, title)
    try:
        text = page.get()
    except Exception as e:
        print("There was a problem: " + str(e))
        return 0

    text = text + "\n\nHello <!--automated edit-->"
    page.text = text
    try:
        page.save("Saving test edit")
        print("Page has been saved")
        return 1
    except:
        print("There was a problem!")
        return 0

def load_wikidata_item(site, item_id):
    """
    This loads an Item and prints some of information about it. 
    """
    item = pywikibot.ItemPage(site, item_id)
    item_title = item.title()
    print("The item title is: " + item_title)

    item_dict = item.get()

    try:
        print('Name: ' + item_dict['labels']['en'])
    except:
        print("There was a problem!")
        return 0

def add_claim_to_item(repo, item_id, prop_id, value, summary):
    """
    This adds new claim to an Item.
    """
    datatype = pywikibot.PropertyPage(repo, prop_id).type
    if datatype == 'wikibase-item':
        value = pywikibot.ItemPage(repo, value)
    elif datatype == 'commonsMedia':
        commons = pywikibot.Site('commons', 'commons')
        value = pywikibot.FilePage(commons, value)
    elif datatype == 'globe-coordinate':
        value = pywikibot.Coordinate(value[0], value[1])
    elif datatype == 'quantity':
        value = pywikibot.WbQuantity(value, site=repo)
    elif datatype == 'time':
        value = pywikibot.WbTime(value)
    elif datatype == 'geo-shape':
        value = pywikibot.WbGeoShape(value)
    elif datatype == 'monolingualtext':
        value = pywikibot.WbMonolingualText(value[0], value[1])
    elif datatype == 'tabular-data':
        value = pywikibot.WbTabularData(value)
    elif datatype == 'url':
        if 'https://' not in value:
            # ensure scheme exists to avoid errors
            value = 'https://' + value
    elif datatype in [ 'math', 'external-id', 'musical-notation' ]:
        pass # raw string value will be used directly
    else:
        raise pywikibot.Error('Unknown datatype: %s' % datatype)

    claim = pywikibot.Claim(repo, prop_id)
    claim.setTarget(value)

    Item = pywikibot.ItemPage(repo, item_id)
    Item.addClaim(claim, summary=summary)
    print('New claim saved!')
    return 1

def add_qualifier(repo, item_id, claim_id, prop_id, target):
    """
    This adds new qualifier to an existing claim
    @param repo DataSite
    @param item_id entity id where to do the work
    @param prop_id the propety id of the claim to add qualifier on
    @param claim_id the propety id of the claim (qualifier) to add
    @param target value of the claim
    """
    item = pywikibot.ItemPage(repo, item_id)
    claims = item.get()['claims']
    claim = claims.get(claim_id)[0] or None

    if not claim:
        return 0

    try:
        qualifier = pywikibot.Claim(repo, prop_id)
        qualifier.setTarget(target)
        claim.addQualifier(qualifier, summary=u'Adding a qualifier.')
        return 1
    except ValueError:
       return 0

def add_reference(repo, item_id, claim_id, rep_type, value):
    """
    This adds new qualifier to an existing claim
    @param repo: DataSite
    @param item_id: entity id where to do the work
    @param prop_id: the propety id of the claim to add qualifier on
    @param claim_id: the propety id of the claim (qualifier) to add
    @param rep_type: the ref form (reference URL, stated in, etc)
    @param value: value of the reference
    """
    item = pywikibot.ItemPage(repo, item_id)
    claims = item.get()['claims']
    claim = claims.get(claim_id)[0] or None

    if not claim:
        return 0

    try:
        reference = pywikibot.Claim(repo, ref_type)
        reference.setTarget(value)
        claim.addSource(reference, summary=u'Adding reference.')
        return 1
    except ValueError:
       return 0


"""RUNNING SOME FUNCTIONS OF THE SCRIPT"""
if __name__ == '__main__':
    enwiki = pywikibot.Site('en', 'wikipedia')
    wikidata = enwiki.data_repository()

    wikidata.login() # Credentials in user-config.py

    # Print the content of the page 
    print_outreachy_page(wikidata, 'User:Ammarpad/Outreachy 1')

    # MacBook:userscripts Ammar$ python
    # Python 3.8.0 (v3.8.0:fa919fdf25, Oct 14 2019, 10:23:27)
    # [Clang 6.0 (clang-600.0.57)] on darwin
    # Type "help", "copyright", "credits" or "license" for more information.
    # >>> import outreachyscript
    # >>> import pywikibot
    # >>> enwiki = pywikibot.Site('en', 'wikipedia')
    # >>> wikidata = enwiki.data_repository()
    # >>> outreachyscript.print_outreachy_page(wikidata, 'User:Ammarpad/Outreachy 1')
    # (Long text string printed here)

    # Append Hello 
    # https://www.wikidata.org/w/index.php?title=User:Ammarpad/Outreachy_1&diff=prev&oldid=1393622205&diffmode=source
    append_hello(wikidata, 'User:Ammarpad/Outreachy 1')

    # MacBook:userscripts Ammar$ python
    # Python 3.8.0 (v3.8.0:fa919fdf25, Oct 14 2019, 10:23:27)
    # [Clang 6.0 (clang-600.0.57)] on darwin
    # Type "help", "copyright", "credits" or "license" for more information.
    # >>> import outreachyscript
    # >>> import pywikibot
    # >>> enwiki = pywikibot.Site('en', 'wikipedia')
    # >>> wikidata = enwiki.data_repository()
    # >>> outreachyscript.append_hello(wikidata, 'User:Ammarpad/Outreachy 1')
    # Page [[wikidata:User:Ammarpad/Outreachy 1]] saved
    # Page has been saved
    # 1
    # >>>

    # Load sandbox item. Print its name and English label
    load_wikidata_item(wikidata, 'Q4115189')

    # MacBook:userscripts Ammar$ python
    # Python 3.8.0 (v3.8.0:fa919fdf25, Oct 14 2019, 10:23:27)
    # [Clang 6.0 (clang-600.0.57)] on darwin
    # Type "help", "copyright", "credits" or "license" for more information.
    # >>> import outreachyscript
    # >>> import pywikibot
    # >>> enwiki = pywikibot.Site('en', 'wikipedia')
    # >>> wikidata = enwiki.data_repository()
    # >>> outreachyscript.load_wikidata_item(wikidata, 'Q4115189')
    # The item title is: Q4115189
    # Name: Wikidata Sandbox
    # >>>

    # Add claim (prop: P31, value: Q5) to sandbox item (Q4115189)
    # https://www.wikidata.org/w/index.php?title=Q4115189&diff=prev&oldid=1393629723&diffmode=source
    add_claim_to_item(wikidata, 'Q4115189', 'P31', 'Q5')

    # MacBook:userscripts Ammar$ python
    # Python 3.8.0 (v3.8.0:fa919fdf25, Oct 14 2019, 10:23:27)
    # [Clang 6.0 (clang-600.0.57)] on darwin
    # Type "help", "copyright", "credits" or "license" for more information.
    # >>> import outreachyscript
    # >>> import pywikibot
    # >>> enwiki = pywikibot.Site('en', 'wikipedia')
    # >>> wikidata = enwiki.data_repository()
    # >>> outreachyscript.add_claim_to_item(wikidata, 'Q4115189', 'P31', 'Q5')
    # New claim saved!
    # >>>
