# OutreachyProject
A collection of python modules to work with wikibase structured data and Wikipedia articles. All the modules require Python 3.7.x and [Pywikibot package](https://github.com/wikimedia/pywikibot), additionally, `fix_netflix_id_mismatch.py` requires [BeautifulSoup library](https://pypi.org/project/beautifulsoup4/).

They are not much cohesive now and some parts are heavily personalized to my local environment or use hardcoding where not necessary, as this is both work-in-progress and proof-of-concept. The main project aim is to eventually coalesce and refactor them into a robust, reusable and extensible script or set of scripts to help in continuous [synchronization of data between Wikidata and Wikipedias](https://phabricator.wikimedia.org/T276329).

1. **outreachyscript.py:**
   - This is the initial module created. It has functions to play with the DataSite/Wikidata, (print content of a page, load wikibase Item, append text to a page e.t.c). It also has functions to actually edit the content pages, add a claim to an
   Item, – with datatype handling – add a reference as well as qualifiers.
2. **get_statements.py:**
   - This module has a single function to search an article and attempts to get where a certain statement is used.
3. **get_statements2.py:**
   - Improved version of `get_statements.py`. This has more detailed logic for elaborate search including through wikitext
 nesting logic, templates and links. It also has a function to check the DataSite and determine whether an Item already has a particular claim.
3. **add_statements.py:**
   - This module has functions to walk through list of pages and associated regex hint to search through their source texts, extract a statement and add it to the Item of the page in the DataSite. Also works for qualifiers and references.
5. **base\_import\_script.py:**
   - Module with functions to retrieve all pages from a Wikipedia category and also to add multiple claims to multiple Item on the DataSite. This module provides base functions needed by both `import_enwiki_netflix_id.py` and `import_enwiki_soundcloud_id.py`
6. **search\_terms\_for\_qids.py:**
   - This module has two functions to search for Item IDs of Wikipedia pages on the repo site. A function that takes list of pages that already have Item page and a function that queries list of unconnected pages and attempt to figure the right ID for them through entity search API.
7. **import\_enwiki\_netflix\_id.py:**
   - This module work is to loop through a list of  English Wikipedia pages, extract their Netflix identifiers (`P1874`) through grepping the source text and add the found IDs to the respective data items of the pages.
8. **import\_enwiki\_soundcloud\_id.py:**
   - This module work is similar to that for `import_enwiki_netflix_id.py`. It loops through a list of  English Wikipedia pages, extract their SoundCloud identifiers (`P3040`) through grepping the source text and add the found IDs to the respective data items of the pages.
9. **fix\_netflix\_id_mismatch.py:**
   - This module has functions to detect and attempt to resolve the Netflix ID disparity between Wikipedia and Wikidata as recorded in [this Wikipedia maintenance category](https://en.wikipedia.org/wiki/Category:Netflix_title_ID_different_from_Wikidata).
