#!/usr/bin/env python

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

def add_claim_to_item(site, item_id, prop, value):
    """
    This adds new claim to an Item.
    """
    item = pywikibot.ItemPage(site, value)
    claim = pywikibot.Claim(site, prop)
    claim.setTarget(item)

    base_item = pywikibot.ItemPage(site, item_id)
    base_item.addClaim(claim, summary='Adding test claim (automated edit)')
    print('New claim saved!')



enwiki = pywikibot.Site('en', 'wikipedia')
wikidata = enwiki.data_repository()
# Print the content of the page 
print_outreachy_page(wikidata, 'User:Ammarpad/Outreachy 1')

# Append Hello 
# https://www.wikidata.org/w/index.php?title=User:Ammarpad/Outreachy_1&diff=prev&oldid=1393622205&diffmode=source
append_hello(wikidata, 'User:Ammarpad/Outreachy 1')


# Load sandbox item. Print its name and English label
load_wikidata_item(wikidata, 'Q4115189'):

# Add claim (prop: P31, value: Q5) to sandbox item (Q4115189)
# https://www.wikidata.org/w/index.php?title=Q4115189&diff=prev&oldid=1393629723&diffmode=source
add_claim_to_item(wikidata, 'Q4115189', 'P31', 'Q5')