#!/usr/bin/env python3
'''
Medal website has a typo in Ireland that is hardcoded here.
If they fix it, Ramon gets no points for them. 
Done is better than Perfect
'''

import yaml

namelist = yaml.load(open('options.yaml', 'r'), Loader=yaml.SafeLoader)

#############################################################################_80
################################################################################
################################################################################

def run_main(infile='standings.txt', values={}, players={}, countries={},
    **kwargs):
    import csv
    import os

    #_initialize all country and player objects
    c_objs = [Country(cod, nam, cos) for (cod, nam, cos) in countries]
    p_objs = [Player(name) for name in players.keys()]

    #_pull in scores for all countries listed in scraped webpage
    with open(infile, 'r') as f:

        webpage_data = csv.reader(f, delimiter=',')

        for country_name, g, s, b in webpage_data:
            g, s, b = [int(o) for o in (g,s,b)]
            try:
                country = c_objs[index(country_name, 'long_name', c_objs)]
            except ValueError:
                #_ignore countries that we don't have costs for
                pass
            country.gold = g  
            country.silver = s
            country.bronze = b
            country.total = g + s + b 
            country.score = g*values['gold'] + s*values['silver'] \
                    + b*values['bronze']

    #_assign countries to players 
    for player in p_objs:
        player.countries = [c_objs[index(code, 'code', c_objs)] 
                for code in players[player.name]]

    #_build a list of lists containing current player scores by country
    scoreboard(p_objs, **kwargs)
##  value_rank(c_objs, **kwargs)

#############################################################################_80
#_SUBROUTINES_##################################################################
################################################################################

def send_to_discord(message, discord_auth='', channels={},
    channel_name='', **kwargs):
    import requests
    payload = {  
        'data'      : { 'content' : message }, 
        'headers'   : { 'authorization' : discord_auth }
        }
    r = requests.post(channels[channel_name], **payload)

def scoreboard(players, nmax=8, **kwargs):
    ''' create scoreboard and post to discord '''

    #_create list of lists to couple player names to rank 
    rank = []
    for i, player in enumerate(players):
        rank.append([player.name, player.total_score()])

    #_sort rankings
    rank = sorted(rank, key=lambda l:l[1], reverse=True)

    #_setup output table format for discord
    hdr = ['PLAYER'] + ['ACT{}'.format(n+1) for n in range(nmax)] + ['tot']
    fmt = '{:10}' + ''.join(['{:<5}' for n in range(nmax)]) + '{:<5}'
    table = '```\n' + fmt.format(*hdr) + '\n'
    for i, (player_name, rank) in enumerate(rank):
        player = players[index(player_name, 'name', players)]
        row = [player.name] 
        [row.append(c.score) for c in player.countries]
        while len(row) < nmax + 1: row.append('')
        row.append(player.total_score())
        table += fmt.format(*row)
        table += '    ' + ' '.join([c.code for c in player.countries]) + '\n'
    table += '```'
    print(table)
    send_to_discord(table, **kwargs)

def value_rank(countries, **kwargs):
    ''' calculate which countries provide the most points per credit '''
    rank = []
    for country in countries:
        ppc = float(country.score) / country.cost
        rank.append([country.code, ppc])
    rank = sorted(rank, key=lambda l:l[1], reverse=True)

    table = '```Country PPC\n'
    fmt = '{:8}{:.2f}\n'
    for i, (code, ppc) in enumerate(rank[:10]):
        table += fmt.format(code, ppc)
    table += '```'
    print(table)
    send_to_discord(table, **kwargs)

def index(value, attribute, objects):
    ''' 
    attribute   str,    field to look through
    value       str,    desired attribute value
    objects     list,   list of objects to search
    return      int,    index of location in list
    '''
    return [getattr(o, attribute) for o in objects].index(value)

#############################################################################_80
#_CLASSES_######################################################################
################################################################################

class Country(object):
    ''' let's pretend this is oo for a second '''
    def __init__(self, code, long_name, cost, **kwargs):
        self.cost = cost 
        self.code = code
        self.long_name = long_name
        self.gold = 0
        self.silver = 0
        self.bronze = 0
        self.total = 0
        self.score = 0

class Player(object):
    ''' participant and data for league '''
    def __init__(self, name, **kwargs):
        self.name = name
        self.countries = []
    
    def total_score(self):
        return sum([c.score for c in self.countries])

if __name__ == '__main__':
    run_main(**namelist)
