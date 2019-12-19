#!/usr/bin/python
# -*- coding: utf-8 -*-

#Josquin Debaz debaz@ehess.fr @josquindebaz
#2019-04-26

# Licence GPL3
# Copyright (c) 2019 Josquin Debaz @josquindebaz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import re
import os
import json
import operator

def toP1(entry, filename):
    d = re.split(" ", entry[u'createdAt'])

    j = re.split('-', d[0])
    s = re.sub(":", "", d[1])
    radical = re.sub('.*/', '', os.path.splitext(filename)[0])
    fn = "%s-%s%s%s-%s-" % (radical,
        j[0][2:4], j[1], j[2], s)
    fn += entry['reference']
    title = entry[u'title']
    
    contentTXT = u"%s\r\n.\r\n\r\n" % title
    for r in entry["responses"]:
        if r['questionId'] == 'UXVlc3Rpb246MTQ5':
            Q = r["questionTitle"]
            R = r["value"]
            #contentTXT += "%s.\r\n\r\n" % Q
            contentTXT += "%s\r\n.\r\n" % R 

        with open("corpus/%s.txt" % fn, "w") as F:
            F.write( contentTXT.encode('cp1252', errors='xmlcharrefreplace') )

        with open("corpus/%s.ctx" % fn, "w") as F:
            date = "%s/%s/%s" % (j[2], j[1], j[0])
            titre = title.encode('cp1252', errors='ignore')
            if not entry[u'authorType']:
                statut = ""
            else:
                statut = entry[u'authorType'].encode('cp1252', errors='ignore')
            contenu_ctx = ["fileCtx0005", 
                titre,   #titre
                entry['reference'],#auteur
                "", #narrateur
                "",#dest 
                date, 
                radical,#support
                "GDN", #type support
                "", #obs
                statut, #statut
                entry['authorZipCode'],#loc
                "", #CL1
                "", #CL2 
                "n", "n", 
                u"REF_HEURE:%s"%d[1]]

            contenu_ctx = map(lambda x: "%s\r\n"%x, contenu_ctx) 
            F.writelines( contenu_ctx )
 

if __name__ == '__main__':
    D = {}
    filename  = "jsons/LA_TRANSITION_ECOLOGIQUE.json"
    with open(filename) as f:
        for cline, item in enumerate(json.load(f)[0:]):
            for r in item['responses']:
                if r['questionId'] == 'UXVlc3Rpb246MTQ5':
                    if (r['value']):
                        s = len(r['value']) 
                        d = re.split(" ", item[u'createdAt'])[0]
                        if d not in D.keys():
                            D[d] = []
                        D[d].append([s, item])
    for day, liste in D.iteritems():
        liste = sorted(liste, key=operator.itemgetter(0), reverse=True)
        n = int(len(liste) * float(3.8112661) / 100)
        for item in liste[:n]:
            toP1(item[1], filename)


