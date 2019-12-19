#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import QGovParser

import glob
import json
import re
import os
import datetime

  
def getQCodeFor(content):
    Id = content["id"] 
    Tit = content["title"] 
    return "%s %s"%(Id, Tit)


def toP1(entry, filename):
    d = re.split(" ", entry[u'createdAt'])

    j = re.split('-', d[0])
    s = re.sub(":", "", d[1])
    radical = re.sub('.*/', '', os.path.splitext(filename)[0])
    fn = "%s-%s%s%s-%s-" % (radical,
        j[0][2:4], j[1], j[2], s)
    fn += entry['reference']
    title = entry[u'titre']
    # entry['authorZipCode']
    
    contentTXT = u"%s\r\n.\r\n\r\n" % title
    for r in entry["responses"]:
        Q = getQ(r["question"])
        R = r["value"]
        if R not in [None, '{"labels":[],"other":null}']:
            contentTXT += "%s.\r\n\r\n" % Q
            if re.search('{"label', R):
                lab, oth = re.split(',"other"', r["value"])
                choices = re.search('"labels":\[(.*)\]', lab).group(1)
                if (choices):
                    spl = re.split('",', choices)
                    if len(spl) == 1:
                        contentTXT += "%s" % (re.sub('"', '', choices))
                    else:
                    #mulitple answer
                        contentTXT += "\r\n".join(sorted([re.sub('"', '', el)\
                            for el in spl]) )
                    contentTXT += "\n.\n"
                other = re.search(':(.*)}', oth).group(1)
                if other != "null":
                    contentTXT += "\r\n%s\r\n.\r\n" %  re.sub('"', '', other)
            else:
                contentTXT += "%s\r\n.\r\n" % R 
            contentTXT += "\r\n" 

    if len(contentTXT) > 1000:
        
        with open("corpus/%s.txt" % fn, "w") as F:
            F.write( contentTXT.encode('cp1252', errors='xmlcharrefreplace') )
        with open("corpus/%s.ctx" % fn, "w") as F:
            date = "%s/%s/%s" % (j[2], j[1], j[0])
            contenu_ctx = ["fileCtx0005", 
                "%s"% title.encode('cp1252', errors='ignore'), 
                entry['reference'],
                "", "", 
                date, 
                radical,
                "",  "", "",  "", "", "", "n", "n", 
                u"REF_HEURE:%s"%d[1]]

            contenu_ctx = map( lambda x: "%s\r\n"%x, contenu_ctx) 
            F.writelines( contenu_ctx )
   


    




if __name__ == '__main__':
    log = u"%s\n" % str(datetime.datetime.now())
    rslt = QGovParser.comptages()

    jsons = glob.glob("jsons/*.json")
    for filename in jsons[0:]:
        with open(filename) as f:
            #ndjson: loading line by line
            for cline, item in enumerate(json.load(f)):
                rslt.parse(item)

            ##OLD Codefor dump
#            lines = f.readlines()
#            for cline, line in enumerate(lines):
#                item = json.loads(line)
#                rslt.parse(item)
            ##

            #generate a corpus for P1
            #1000 first entries as prospero files
#                if cline < 2000:
#                    toP1(item, filename)


        #log += "%s %d lignes\n" %(filename, cline) 
        log += "%s %d lignes\n" %(filename, cline) 

    log += "\n\n"
    rslt.reportNull()

    for k in sorted(rslt.TxRep.keys()):
        log += u"%s" %k
        if (rslt.TxRep[k][0]): #if not a title
            log +=  u"\n   Taux réponse %s %%\n" % \
                (100 * float(rslt.TxRep[k][0])/sum(rslt.TxRep[k]))
        else:
            log += "\n%s"%("_"*50)

        if k in rslt.Dlabels.keys():
            choices = rslt.Dlabels[k]

            if "autre" in choices.keys():
                autre = choices.pop("autre")
            else:
                autre = None

            s = float(sum(choices.values()))

            #choice results order by value
            for r, v in sorted(choices.items(), 
                    key=operator.itemgetter(1), reverse=True):
                log += "\t%s\n" % (r) 
                log += "\t%s %d (%f %%)\n" % ("*"*int(round(100*v/s)), v, (100*v/s) )

            if (autre):
                log += "\n\tautre %d\n" % (autre)
                log += textreportOpen(rslt.Dothers[k])

        if k in rslt.Douvertes.keys():
            log += textreportOpen(rslt.Douvertes[k])
            #pass

        log += "\n\n"
                
    #write summary
    with open("result.txt", 'w') as F:
        F.write(log.encode("utf-8"))
            



    #csv of length of answer of open questions
    toutes_longueurs = []
    Dlength = {}
    for Q, R in rslt.Douvertes.iteritems():
        q = u"Q_%s"% Q[0:3]
        Dlength[q]  = {}
        longueurs = [ len(re.split("\s*", r)) for r in R ]
        for longueur in list(set(longueurs)): #sans doublon
            Dlength[q][longueur] = longueurs.count(longueur) 
            if longueur not in toutes_longueurs:
                toutes_longueurs.append(longueur)

    with open("lengthOpens.csv", "w") as F:
        firstline = u","
        firstline += u','.join( sorted(Dlength.keys()) )
        F.write(u"%s\n" % firstline)

        for longueur in sorted(toutes_longueurs):
            line = u'%d,'% longueur
            for q in sorted(Dlength.keys()): 
                if longueur in Dlength[q].keys():
                    line += u"%d,"%(Dlength[q][longueur])
                else:
                    line += u","
            F.write("%s\n"%line[:-1])

