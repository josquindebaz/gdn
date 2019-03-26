#!/usr/bin/python
# -*- coding: utf-8 -*-

#Josquin Debaz debaz@ehess.fr @josquindebaz
#2019-02-14

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
import datetime
import json
import operator

if __name__ == '__main__':
    log = u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">\n<head>\n<meta http-equiv="content-type" content="text/html; charset=UTF-8"  />\n</head>\n<body>\n<p>%s</p>\n<ul>\n' % str(datetime.datetime.now())
    rslt = QGovParser.comptages()

    jsons = glob.glob("jsons/*.json")
    for filename in jsons[0:]:
        #print(filename)
        with open(filename) as f:
            #ndjson: loading line by line
            #error in raw_decode obj, end = self.scan_once(s, idx) ValueError: Expecting object:
            #because missing a ] at the end of file
            #sed -e "$ a\]" XYZ.json > xyz.json
            for cline, item in enumerate(json.load(f)):
                rslt.parse(item)

        log += " <li>%s %d lignes</li>\n" %(filename, cline) 

    log += "</ul>\n\n"
    rslt.reportNull()

    for k in sorted(rslt.TxRep.keys()):
        #les questions titre ne sont pas dans le json du gouv
        log +=  u"  <h2>%s</h2>\n<p>Taux de réponse %s %%</p>\n" % (k,
            (100 * float(rslt.TxRep[k][0])/sum(rslt.TxRep[k])) )

        if k in rslt.Dlabels.keys():
            choices = rslt.Dlabels[k]

            if "autre" in choices.keys():
                autre = choices.pop("autre")
            else:
                autre = None

            if (autre):
                s = float(autre + sum(choices.values()))
            else:
                s = float(sum(choices.values()))

            #choice results order by value
            for r, v in sorted(choices.items(), 
                    key=operator.itemgetter(1), reverse=True):
                log += "<p>%s</p>\n" % (r) 
                log += "<p>%s %d (%f %%)</p>\n" % ("*"*int(round(50*v/s)), 
                    v, (100*v/s) )

            if (autre):
                log += "\n   <h3>autre %d (%f %%)</h3>\n" % (autre, (100*autre/s) )
                log += QGovParser.textreportOpen(rslt.Dothers[k])

        if k in rslt.Douvertes.keys():
            log += QGovParser.textreportOpen(rslt.Douvertes[k])
            #pass

        log += "\n\n"
                
    #write summary
    with open("resume.html", 'w') as F:
        F.write(log.encode("utf-8"))
            


