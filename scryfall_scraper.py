# -*- coding: utf-8 -*-
import requests
import time


def get_scryfall(setUrl='https://api.scryfall.com/cards/search?q=++e:xln'):
    #getUrl = 'https://api.scryfall.com/cards/search?q=++e:'
    #setUrl = getUrl + code.lower()
    setDone = False
    scryfall = []

    while setDone == False:
        setcards = requests.get(setUrl)
        setcards = setcards.json()
        if 'data' in setcards.keys():
            scryfall.append(setcards['data'])
        else:
            setDone = True
            print ('No Scryfall data')
            scryfall = ['']
        time.sleep(.1)    # 100ms sleep, see "Rate Limits and Good Citizenship" at https://scryfall.com/docs/api
        if 'has_more' in setcards.keys():
            if setcards['has_more']:
                setUrl = setcards['next_page']
            else:
                setDone = True
        else:
            print ('Scryfall does not "has_more"')
            setDone = True
    if not scryfall[0] == '':
        import json
        scryfall2 = []
        for cardarray in scryfall:
            for card in cardarray:
                scryfall2.append(card)
        scryfall = convert_scryfall(scryfall2)
        return {'cards': scryfall}
    else:
        return {'cards': []}

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def convert_scryfall(scryfall):
    cards2 = []
    scryfall2 = []
    for card in scryfall:
        if card == "cards" or card == "" or card == []:
            continue
        if 'layout' in card:
            if card['layout'] == 'transform':
                cardNoFaces = {}
                for key in card:
                    if key != 'card_faces':
                        cardNoFaces[key] = card[key]
                cardNoFaces['layout'] = 'double-faced'
                cardNoFaces['names'] = [card['card_faces'][0]['name'], card['card_faces'][1]['name']]
                card1 = merge_two_dicts(cardNoFaces, card['card_faces'][0])
                card2 = merge_two_dicts(cardNoFaces, card['card_faces'][1])
                card1['collector_number'] = card1['collector_number'] + 'a'
                card2['collector_number'] = card2['collector_number'] + 'b'
                scryfall2.append(card1)
                scryfall2.append(card2)
            elif card['layout'] == 'split':
                cardNoFaces = {}
                for key in card:
                    if key != 'card_faces':
                        cardNoFaces[key] = card[key]

                cardNoFaces['names'] = [card['card_faces'][0]['name'], card['card_faces'][1]['name']]

                # print("CZZ: {}".format(cardNoFaces))
                # print("CZZ: {}".format(card))

                card1 = merge_two_dicts(cardNoFaces, card['card_faces'][0])
                card2 = merge_two_dicts(cardNoFaces, card['card_faces'][1])
                card1['collector_number'] = str(card['collector_number']) + "a"
                card2['collector_number'] = str(card['collector_number']) + "b"
                scryfall2.append(card1)
                scryfall2.append(card2)
            else:
                scryfall2.append(card)
        else:
            scryfall2.append(card)    
    scryfall = scryfall2
    for card in scryfall:
        card2 = {}
        card2['cmc'] = int(card['cmc'])
        if 'names' in card:
            card2['names'] = card['names']
        if 'mana_cost' in card.keys():
            card2['manaCost'] = card['mana_cost'].replace(
                '{', '').replace('}', '')
        else:
            card2['manaCost'] = ''
        card2['name'] = card['name']
        card2['number'] = card['collector_number']
        card2['rarity'] = card['rarity'].replace(
            'mythic', 'mythic rare').title()
        if 'oracle_text' in card.keys():
            card2['text'] = card['oracle_text'].replace(
                u"\u2014", '-').replace(u"\u2212", "-")
        else:
            card2['text'] = ''
        if 'image_uri' in card:
            card2['url'] = card['image_uri']
        elif 'image_uris' in card:
            if 'large' in card['image_uris']:
                card2['url'] = card['image_uris']['large']
            elif 'normal' in card['image_uris']:
                card2['url'] = card['image_uris']['normal']
            elif 'small' in card['image_uris']:
                card2['url'] = card['image_uris']['small']
                
        if not 'type_line' in card:
            card['type_line'] = 'Unknown'
        card2['type'] = card['type_line'].replace(u'—', '-')
        cardtypes = card['type_line'].split(u' — ')[0].replace('Legendary ', '').replace('Snow ', '')\
            .replace('Elite ', '').replace('Basic ', '').replace('World ', '').replace('Ongoing ', '')
        cardtypes = cardtypes.split(' ')
        if u' — ' in card['type_line']:
            cardsubtypes = card['type_line'].split(u' — ')[1]
            if ' ' in cardsubtypes:
                card2['subtypes'] = cardsubtypes.split(' ')
            else:
                card2['subtypes'] = [cardsubtypes]
        if 'Basic Land' in card['type_line']:
            card2['rarity'] = "Basic Land"
        if 'Legendary' in card['type_line']:
            if 'supertypes' in card2.keys():
                card2['supertypes'].append('Legendary')
            else:
                card2['supertypes'] = ['Legendary']
        if 'Snow' in card['type_line']:
            if 'supertypes' in card2.keys():
                card2['supertypes'].append('Snow')
            else:
                card2['supertypes'] = ['Snow']
        if 'Elite' in card['type_line']:
            if 'supertypes' in card2.keys():
                card2['supertypes'].append('Elite')
            else:
                card2['supertypes'] = ['Elite']
        if 'Basic' in card['type_line']:
            if 'supertypes' in card2.keys():
                card2['supertypes'].append('Basic')
            else:
                card2['supertypes'] = ['Basic']
        if 'World' in card['type_line']:
            if 'supertypes' in card2.keys():
                card2['supertypes'].append('World')
            else:
                card2['supertypes'] = ['World']
        if 'Ongoing' in card['type_line']:
            if 'supertypes' in card2.keys():
                card2['supertypes'].append('Ongoing')
            else:
                card2['supertypes'] = ['Ongoing']
        card2['types'] = cardtypes
        if 'color_identity' in  card.keys():
            card2['colorIdentity'] = card['color_identity']
        if 'colors' in  card.keys():
            if not card['colors'] == []:
                card2['colors'] = []
                if 'W' in card['colors']:
                    card2['colors'].append("White")
                if 'U' in card['colors']:
                    card2['colors'].append("Blue")
                if 'B' in card['colors']:
                    card2['colors'].append("Black")
                if 'R' in card['colors']:
                    card2['colors'].append("Red")
                if 'G' in card['colors']:
                    card2['colors'].append("Green")
                #card2['colors'] = card['colors']
        if'all_parts' in  card.keys():
            card2['names'] = []
            for partname in card['all_parts']:
                card2['names'].append(partname['name'])
        if'power' in  card.keys():
            card2['power'] = card['power']
        if'toughness' in  card.keys():
            card2['toughness'] = card['toughness']
        if'layout' in  card.keys():
            if card['layout'] != 'normal':
                card2['layout'] = card['layout']
        if'loyalty' in  card.keys():
            card2['loyalty'] = card['loyalty']
        if'artist' in  card.keys():
            card2['artist'] = card['artist']
        # if'source' in  card.keys():
        #    card2['source'] = card['source']
        # if'rulings' in  card.keys():
        #    card2['rulings'] = card['rulings']
        if'flavor_text' in  card.keys():
            card2['flavor'] = card['flavor_text']
        if'multiverse_id' in  card.keys():
            card2['multiverseid'] = card['multiverse_id']

        cards2.append(card2)

    return cards2


def smash_mtgs_scryfall(mtgs, scryfall):
    for mtgscard in mtgs['cards']:
        cardFound = False
        for scryfallcard in scryfall['cards']:
            if scryfallcard['name'] == mtgscard['name']:
                for key in scryfallcard:
                    if key in mtgscard:
                        if not mtgscard[key] == scryfallcard[key]:
                            try:
                                print ("%s's key %s\nMTGS    : %s\nScryfall: %s" % (mtgscard['name'], key, mtgscard[key], scryfallcard[key]))
                            except:
                                print ("Error printing Scryfall vs MTGS debug info for " + mtgscard['name'])
                                pass
                cardFound = True
        if not cardFound:
            print ("MTGS has card %s and Scryfall does not." % mtgscard['name'])
    for scryfallcard in scryfall['cards']:
        cardFound = False
        for mtgscard in mtgs['cards']:
            if scryfallcard['name'] == mtgscard['name']:
                cardFound = True
        if not cardFound:
            print ("Scryfall has card %s and MTGS does not." % scryfallcard['name'])

    return mtgs