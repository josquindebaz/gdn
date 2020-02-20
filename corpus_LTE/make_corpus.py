#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Create a corpus for Prospero 1 from a json file of the Grand débat national
Josquin Debaz debaz@ehess.fr @josquindebaz
2019-04-26
2020-02-20

 Licence GPL3
 Copyright (c) 2019-2020 Josquin Debaz @josquindebaz

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, version 3 of the License.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
"""

import re
import os
import json
import operator


FILENAME = "../jsons/LA_TRANSITION_ECOLOGIQUE.json"
#5 000 texts -> 3.8112661
PROPORTION = 10000 / 131190 * 100
FOLDER = "LTEQ5"

def utf_to_latin(text):
    """Convert utf to latin"""
    return text.encode('cp1252', 'xmlcharrefreplace')

def to_p1(entry, radical):
    """write txt and ctx for an answer, with radical base for filenames"""
    day_time = re.split(" ", entry[u'createdAt'])
    date = re.split('-', day_time[0])
    namebase = "%s_%s_"%(radical, entry['reference'])
    namebase += "%s%s%s%sx-"%(date[0][2:4],
                             date[1],
                             date[2],
                             day_time[1][:2])
    if os.path.isfile("%s/%s.txt" % (FOLDER, namebase)):
        print("doublon", namebase)

    txt_content = "%s\r\n.\r\n\r\n" % entry['title']

    for values in entry["responses"]:
        if values['questionId'] == 'UXVlc3Rpb246MTQ5':
            #question = values["questionTitle"]
            response = values["value"]
            txt_content += "%s\r\n" % response

        with open("%s/%s.txt"%(FOLDER, namebase), "wb") as txt_file:
            txt_file.write(utf_to_latin(txt_content))

        ctx_date = "%s/%s/%s" % (date[2], date[1], date[0])
        if not entry['authorType']:
            statut = ""
        else:
            statut = entry['authorType']
        ctx_content = ["fileCtx0005",
                       entry['title'],#titre
                       entry['reference'],#auteur
                       "", #narrateur
                       "",#destinataire
                       ctx_date,
                       FILENAME,#support
                       "Grand Débat National", #type support
                       "Size ranking limitation %s"%PROPORTION, #obs
                       statut, #statut
                       entry['authorZipCode'],#localisation
                       "", #CL1
                       "", #CL2
                       "n",
                       "n",
                       "REF_HEURE:%s"%day_time[1]]

        ctx_content = utf_to_latin("\r\n".join(ctx_content))

        with open("%s/%s.ctx"%(FOLDER, namebase), "wb") as ctx_file:
            ctx_file.write(ctx_content)

def json_to_dict(content):
    """transfer the json content to a dictionary:
        date-> [[size1, answer1], [size2, answer2], ...]"""
    answers = {}
    for item in content:
        for answer in item['responses']:
            if answer['questionId'] == 'UXVlc3Rpb246MTQ5':
                if answer['value']:
                    answer_size = len(answer['value'])
                    answer_date = re.split(" ", item[u'createdAt'])[0]
                    if answer_date not in answers.keys():
                        answers[answer_date] = []
                    answers[answer_date].append([answer_size, item])
    return answers

if __name__ == '__main__':
    print("Opening ", FILENAME)
    with open(FILENAME) as f_pointer:
        CONTENT = json.load(f_pointer)
        print("Size ", len(CONTENT))
        ANSWERS = json_to_dict(CONTENT)
    for day, answer_list in ANSWERS.items():
        answer_list = sorted(answer_list,
                             key=operator.itemgetter(0),
                             reverse=True)
        final_size = int(len(answer_list) * float(PROPORTION) / 100)
        for answ in answer_list[:final_size]:
            #write n=final_size answers to .txt and .ctx for P1
            to_p1(answ[1], "LTEQ5")
