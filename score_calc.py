#!/usr/bin/env python3
'''
Medal website has a typo in Ireland that is hardcoded here.
If they fix it, Ramon gets no points for them. 
Done is better than Perfect
'''

import os
import csv
import numpy as np
import requests
import yaml

namelist = yaml.load(open('options.yaml', 'r') Loader=yaml.SafeLoader)

#############################################################################_80
################################################################################
################################################################################

def run_main(infile='standings.txt', values={}, players={}, countries=[],
    channel_name='test', channels={}, discord_auth='', nmax=8, **kwargs):

    #_pull in scores for all countries listed in scraped webpage
    scores = [0] * len(countries)
    countries_available = []
    with open(infile, 'r') as f:
        data = csv.reader(f, delimiter=',')
        for country, g, s, b in data:
            countries_available.append(country)
            if country in countries:
                scores[countries.index(country)] = values['gold']*int(g) + \
                values['silver']*int(s) + values['bronze']*int(b)
  
    #_check if all countries are in webpage data
    bail = False
    for country in countries:
        if country not in countries_available:
            print("MISSING {}".format(country))
            bail = True
    if bail:
        os._exit(1)

    #_build a list of lists containing current player scores by country   
    ordered_names = players.keys()
    score_array = [ [name] for name in ordered_names ]
    for i, entry in enumerate(players.items()):
        player, picks = entry

        total_score = 0
        for j in range(nmax):
            try:
                country_code = picks[j]
            except IndexError: #_less than 8 picks
                score_array[i].append(0)
                continue

            try:
                score_array[i].append(scores[country_code])
                total_score += scores[country_code]
            except IndexError:
                print('MISSING COUNTRY: {}'.format(country_code))

        score_array[i].append(total_score)

    #_convert to numpy array and sort by current leader
    score_array = np.array(score_array)
    score_array = score_array[score_array[:,-1].argsort()[::-1]]

    #_setup output table format for discord
    hdr = ['chump', 'act1', 'act2', 'act3', 'act4', 'act5', 'act6', 'act7', 'act8', 'tot']
    fmt = '{:10} {:5} {:5} {:5} {:5} {:5} {:5} {:5} {:5} {:5}'
    table = '```' + fmt.format(*hdr) + '\n'
    for i, name in enumerate(ordered_names):
        table += fmt.format(*score_array[i,:])
##      table += ' '.join([countries[n] for n in players[name]])
        table += '\n'
    table += '```'

    print(table)

    #_send to discord
    payload = {  
        'data' : {'content' : table}, 
        'headers': {'authorization' : discord_auth }}
    r = requests.post(channels[channel_name], **payload)

if __name__ == '__main__':
    run_main(**namelist)
