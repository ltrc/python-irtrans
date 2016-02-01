#!/usr/bin/env python 
# -*- coding: utf-8 -*-

#Copyright (C) 2015 Irshad Ahmad Bhat


import os
import re
import sys

from ._utils import SSFReader
from .ind2rom import IR_Transliterator
from .rom2ind import RI_Transliterator

class transliterator():

    def __init__(self, format_='text', source='hin', target='eng', ssf_type=None, nested=False):
        self.nested = nested
        self.format_ = format_
        self.ssf_type = ssf_type
        if source != "eng":
            irt = IR_Transliterator(source)
            self.transform = irt.transliterate
        else:
            rit = RI_Transliterator(target)
            self.transform = rit.transliterate

    def convert_ssf(self, sentence):
        """Convert SSF data"""
        consen = str()
        obj = SSFReader(sentence)
        obj.getAnnotations()
        for node,order in zip(obj.nodeList, obj.fs_order):
            if self.ssf_type == 'intra' or (self.ssf_type == 'inter' and not node.id.isdigit()):
                name = self.transform(node.name) if node.name not in self.special else node.name
                head = self.transform(node.head) if self.nested else node.head
            else:
                name = node.name
                head = self.transform(node.head) if node.head not in self.special else node.head
            if self.ssf_type == 'intra':
                parent = self.transform(node.parent) if node.parent not in self.special else node.parent
            else:
                parent = node.parent
            wordForm = self.transform(node.wordForm) if node.wordForm not in self.special else node.wordForm
            dmrel_ = 'dmrel' if node.dmrel else 'drel'
            ssfNode = [node.id, wordForm, node.posTag]
            if isinstance(node.af, tuple):
                nL = node.af
                lemma = self.transform(nL.lemma) if nL.lemma not in self.special else nL.lemma
                vib = self.transform(nL.vib) if nL.vib not in self.special else nL.vib
                features = ",".join((lemma, nL.cat, nL.gen, nL.num, nL.per, nL.case, vib, nL.tam))
            else:
                features = node.af
            fs = [
                    "af='%s'" % (features) if node.af else '',
                    "name='%s'" % (name) if name else None,
                    "head='%s'" % (head) if head else None,
                    "chunkId='%s'" % (node.chunkId) if (node.chunkId and node.chunkType == 'head') else None,
                    "chunkType='%s:%s'" % (node.chunkType, node.chunkId) if node.chunkType else None,
                    "posn='%s'" % (node.posn) if node.posn else None,
                    "vpos='%s'" % (node.vpos) if node.vpos else None,
                    "%s='%s:%s'" % (dmrel_, node.drel, parent) if node.drel else None,
                    "coref='%s:%s'" % (node.corel, node.coref) if node.coref else None,
                    "stype='%s'" % (node.stype) if node.stype else None,
                    "voicetype='%s'" % (node.voicetype) if node.voicetype else None,
                    "poslcat='%s'" % (node.poslcat) if node.poslcat else None,
                    "mtype='%s'" % (node.mtype) if node.mtype else None,
                    "troot='%s'" % (node.troot) if node.troot else None,
                    "etype='%s'" % (node.etype) if node.etype else None,
                    "etype_root='%s'" % (node.etype_root) if node.etype_root else None,
                    "emph='%s'" % (node.emph) if node.emph else None,
                    "esubtype='%s'" % (node.esubtype) if node.esubtype else None,
                    "etype_name='%s'" % (node.etype_name) if node.etype_name else None,
                    "agr_num='%s'" % (node.agr_num) if node.agr_num else None,
                    "hon='%s'" % (node.hon) if node.hon else None,
                    "agr_cas='%s'" % (node.agr_cas) if node.agr_cas else None,
                    "agr_gen='%s'" % (node.agr_gen) if node.agr_gen else None #NOTE add node
                  ]
            fs_ = fs[:]
            for idx in order:
                fs.remove(fs_[idx])
                fs.insert(0, fs_[idx])
            fs = "<fs %s>" % (" ".join(filter(None, fs)))
            if node.id:
                consen += "%s\n" %("\t".join(ssfNode+[fs]))
            else:
                consen += "%s\n" %("\t))")

        return consen

    def convert_conll(self, conll):
        """Convert CONLL data"""
        trans_LINES = list()
        if isinstance(conll, unicode):
            conll = conll.encode('utf-8')
        lines = conll.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                trans_LINES.append("")
                continue
            line = line.split("\t")
            if len(line) != 10:
                sys.stderr.write("Warning: dimension mismatch (attributes < 10 or > 10) \n")
            FORM, LEMMA, FEATS = line[1], line[2], line[5].split("|")
            vib_id = [idx for idx,feat in enumerate(FEATS) if feat[:4]=="vib-"][0]
            vib = FEATS[vib_id].lstrip("vib-")
            vib = re.split("([+_0-9]+)", vib)
            vib = " ".join(vib).split()
            if not (FORM[0] == "&" and FORM[-1] == ";"):
                FORM = self.transform(FORM)
            if not (LEMMA[0] == "&" and LEMMA[-1] == ";"):
                LEMMA = self.transform(LEMMA)
            trans_FEATS = [FORM, LEMMA]
            for word in vib:
                if word in ["+", "_"] or word.isdigit():
                  trans_FEATS.append(word)
                  continue
                trans_word = self.transform(word)
                trans_FEATS.append(trans_word)
            line[1] = trans_FEATS[0] if trans_FEATS[0].strip() else "_"
            line[2] = trans_FEATS[1] if trans_FEATS[1].strip() else "_"
            FEATS[vib_id] = "vib-%s" %"".join(trans_FEATS[2:])
            line[5] = "|".join(FEATS)
            trans_LINES.append("%s" %"\t".join(line))
        return "\n".join(trans_LINES)

    def convert(self, line):
        if self.format_=="text":
            return self.transform(line)
        elif self.format_=="ssf":
            self.special = set(['null', 'NULL', 'COMMA', 'SINGLE_QUOTE', '-JOIN'])
            return self.convert_ssf(line)
        elif self.format_=="conll":
            return self.convert_conll(line)
        elif self.format_ in ["bio", "tnt"]:
            trans_LINES = list()
            lines = line.split("\n")
            for line in lines:
                line = line.split()
                if not line:
                    trans_LINES.append("")
                    continue
                FORM = line[0]
                line[0] = self.transform(FORM)
                trans_LINES.append("%s" %"\t".join(line))
            return "\n".join(trans_LINES)
        else: 
            sys.stderr("FormatError: invalid format :: %s\n" %self.format_)
            sys.exit(0)
