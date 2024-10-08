#!/bin/python3
import urllib.request
import json
import re
import time
import xml.etree.ElementTree as ET

# FIXME load these externally
ARCHIDEKT_USERNAME = "Derpthemeus"
COCKATRICE_DECKS_PATH = "/home/matt/.local/share/Cockatrice/Cockatrice/decks"

# TODO support pagination
list_url = "https://archidekt.com/api/decks/cards/?orderBy=-createdAt&owner=%s&ownerexact=true&pageSize=50" % ARCHIDEKT_USERNAME

deck_list = json.loads(urllib.request.urlopen(list_url).read())
for deck_summary in deck_list["results"]:
    deck_e = ET.Element("cockatrice_deck")
    deck_e.set("version", "1")
    name_e = ET.SubElement(deck_e, "deckname")
    name_e.text = deck_summary["name"]
    main_zone_e = ET.SubElement(deck_e, "zone")
    main_zone_e.set("name", "main")
    side_zone_e = ET.SubElement(deck_e, "zone")
    side_zone_e.set("name", "side")

    deck_url = "https://archidekt.com/api/decks/%d/" % deck_summary["id"]
    deck = json.loads(urllib.request.urlopen(deck_url).read())

    categories = dict()
    for category in deck["categories"]:
        categories[category["name"]] = category

    for card in deck["cards"]:
        zone_e = main_zone_e
        included_in_deck = True
        if card["categories"] is not None:
            for category_name in card["categories"]:
                category = categories[category_name]
                if not category["includedInDeck"]:
                	included_in_deck = False
                if category["name"].lower() == "sideboard":
                    zone_e = side_zone_e
        if not included_in_deck:
            continue
        card_e = ET.SubElement(zone_e, "card")
        card_e.set("number", str(card["quantity"]))
        # FIXME is there a way to handle flip cards?
        card_name = card["card"]["oracleCard"]["name"]
        card_e.set("name", card_name)

    clean_name = re.sub("[^a-zA-Z0-9\- _]", "-", deck_summary["name"])
    filename = "%s/archidekt-%s-%s.cod" % (COCKATRICE_DECKS_PATH, ARCHIDEKT_USERNAME, clean_name)
    print("Saving %s/'%s' (%d) to '%s'" % (ARCHIDEKT_USERNAME, deck_summary["name"], deck_summary["id"], filename))
    xml = ET.ElementTree(element=deck_e)
    xml.write(filename)

    # Don't hit the Archidekt API too hard.
    time.sleep(1)
print("Done!")
