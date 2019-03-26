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


import re
import numpy
import operator
import datetime
from collections import Counter

def getQ(content):
    Id = content["questionId"] 
    Tit = content["questionTitle"] 
    return "%s %s"%(Id, Tit)

def typish(items, limit, n):
    return sorted([[len(el), el] for el in items if len(el) >= limit])[0:n]
 
def reportOpen(items):
    l = [len(el) for el in items]
    return max(l), numpy.percentile(l, 25), numpy.median(l), numpy.percentile(l, 75)

def nOccOpen(items):
    data = Counter(items)
    return data.most_common(5)
 
def textreportOpen(items):
    longer, q1, mediane, q3 = reportOpen(items)
    freqmax = nOccOpen(items)
    Medex = typish(items, mediane, 5)
    Q3ex = typish(items, q3, 5)
    Q1ex = typish(items, q1, 5)

    log = u"<p>Tailles : 1er quartile %d caractères | médiane %d | 3e quartile %d | plus longue %d</p>"\
        % (q1, mediane, q3, longer)

    log += u"\n   <h4>5 Exemples 1er quartile :</h4>\n<ul>\n"
    for ex in Q1ex: 
        log += u"<li><i>%s</i></li>\n" % (ex[1])

    log += u"\n</ul>\n<h4>5 Exemples de longueur médiane :</h4>\n<ul>\n"
    for ex in Medex: 
        log += u"<li><i>%s</i></li>\n" % (ex[1])

    log += u"\n</ul>\n    <h4>5 Exemples 3e quartile :</h4>\n<ul>\n"
    for ex in Q3ex: 
        log += u"<li><i>%s</i></li>\n" % (ex[1])

    log += u"\n</ul>\n    <h4>Les 5 formes plus fréquentes :</h4>\n<ul>\n"
    for el in freqmax: 
        log += u"<li><i>%s</i> (%d occurences)</li>\n" % (el[0], el[1]) 

    log += "</ul>\n"
    return log



class comptages(object):
    def __init__(self):
        self.Dlabels = {}
        self.Dothers = {}
        self.Douvertes = {}
        self.listnull = []
        self.listnotnull = []

    def countLabels(self, questionlabels):
        for (q, rs) in questionlabels.iteritems():
            if q not in self.Dlabels.keys():
                self.Dlabels[q] = {}
            for c in rs:
                if type(c) == type([]):
                    if q not in self.Dothers.keys():
                        self.Dothers[q] = [c[1]]
                    else:
                        self.Dothers[q].append( c[1] )
                    c = c[0]
                if c not in self.Dlabels[q].keys():
                    self.Dlabels[q][c] = 1
                else:
                    self.Dlabels[q][c] += 1

    def countOpens(self, questionouvertes):
        for (q, r) in questionouvertes:
            if q not in self.Douvertes.keys():
                self.Douvertes[q] = [r]
            else:
                self.Douvertes[q].append(r)

    def reportNull(self):
        self.TxRep  = {}

        for L in self.listnotnull:
            for q in L:
                if q not in self.TxRep:
                    self.TxRep[q] = [0, 0]
                self.TxRep[q][0] += 1

        for L in self.listnull:
            for q in L:
                if q not in self.TxRep:
                    self.TxRep[q] = [0, 0]
                self.TxRep[q][1] += 1
    
    def parse(self, entry):
        null = []
        notnull = [] 
        questionlabels = {}
        questionouvertes = [] 

        R = entry["responses"]
        for c, r in enumerate(R):
            choice = []

            Q = getQ(r)

            if r["value"] in [None, '{"labels":[],"other":null}']:
                null.append(Q)
            else:
                notnull.append(Q)

                if re.search('{"label', r["value"]):
                #answer by choice
                    lab, oth = re.split(',"other"', r["value"])
                    choices = re.search('"labels":\[(.*)\]', lab).group(1)
                    other = re.search(':(.*)}', oth).group(1)

                    if (choices):
                        spl = re.split('",', choices)
                        if len(spl) == 1:
                            choice.append(re.sub('"', '', choices))
                        else:
                        #mulitple answer
                            choice.append(", ".join(sorted([re.sub('"', '', el)\
                                for el in spl]) ))

                    if other != "null":
                        choice.append(["autre", re.sub('"', '', other)])

                    questionlabels[Q] =  choice 

                #open answer
                else:
                    questionouvertes.append([Q, r["value"]])

        self.listnull.append(null)
        self.listnotnull.append(notnull)

        self.countLabels(questionlabels)
        self.countOpens(questionouvertes)


