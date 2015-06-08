#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# manuscript: generate LaTeX, pdf and docx simultaneously
#
# Nelson Luís Dias
# 2014-02-05T18:40:11 starting
# 2014-02-06T08:35:21 working
# 2014-02-09T13:47:48 all the way up to docx generation
# 2014-02-10T10:59:23 skips verbatim when replacing cross-references
# 2014-02-21T14:21:34 this separate version of manuscript.py fixes a problem with
#                     abnt.cls in-text citations (without parenthesis)
# 2014-02-22T11:26:12 including gpl
# 2014-02-22T11:26:36 now in github
# 2014-02-22T12:57:26 only fix abnt glitch if this is abnt.csl
# 2014-03-03T11:16:21 master extension should be .mns
# 2014-03-16T16:57:18 giving up special treatment of windows utf-8 bad chars
# 2014-08-23T14:50:54 there is still a problem with \ref's that shouldn't be
#                     resolved
# 2015-06-07T13:10:48 getting rid of the mns file
#
# GPL
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------
from os import system
from sys import argv, platform, exit
# ------------------------------------------------------------------------------
# determine once and for all in which OS I am operating
# ------------------------------------------------------------------------------
print(platform)
if platform == "linux" or platform == "darwin" :
   rmcmd = "rm --force "
elif platform == "win32" or platform == "win64" :
   rmcmd = "del/q "
else :
   print("I don't know which OS. Have to stop")
   exit(1)
pass
print(rmcmd)
import re
# -----------------------------------------------------------------------------
# findmepar: a not-very-elegant way to extract lang, bibf and cslf
# -----------------------------------------------------------------------------
def findmepar(line,arg):
   estip = '<!-- '+arg
   begcom = line.find(estip)
   endcom = line.find('-->')
   return(line[begcom+len(estip):endcom].strip())
pass
# -----------------------------------------------------------------------------
# again, a not very elegant (actually a brute force) approach: read the whole
# file just to extract lang, bibf and cslf. then, close file and restart.
# -----------------------------------------------------------------------------
master = argv[1]
# ------------------------------------------------------------------------------
# now open the master, and read:
#
# 2. the language of the project (babel convention)
# 3. the bibliography database (with extension .bib included, bibtex format)
# 4. the bibliography style file (.csl)
# ------------------------------------------------------------------------------
fmaster = open(master,'rt')
nolang = True
nobibf = True
nocslf = True
for line in fmaster:
   if (nolang) and ('<!-- language:' in line):
      lang = findmepar(line,'language:')
      nolang = False
   if (nobibf) and ('<!-- bibliography:' in line):
      bibf = findmepar(line,'bibliography:')
      nobibf = False
   if (nocslf) and ('<!-- citation-style:' in line):
      cslf = findmepar(line,'citation-style:')
      nocslf = False
pass
fmaster.close()
# -------------------------------------------------------------------------------
# the three lines are mandatory
# -------------------------------------------------------------------------------
if nolang:
   print('I did not find a <!-- language: specification')
   exit(1)
if nobibf:
   print('I did not find a <!-- bibliography: specification')
   exit(1)
if nolang:
   print('I did not find a <!-- citation-style: specification')
   exit(1)
# ------------------------------------------------------------------------------
# the main file name (without extension)
# ------------------------------------------------------------------------------
wout = argv[1].find('.txt')
mainf = argv[1][:wout] #(fmaster.readline()).strip()
print(mainf)
print(lang)
print(bibf)
print(cslf)
#exit(1)
# ------------------------------------------------------------------------------
# cleanup latex leftovers
# ------------------------------------------------------------------------------
rmpdf = (rmcmd + " %s.pdf") % mainf
print(rmpdf)
system(rmpdf)
rmtex = (rmcmd + " %s.tex") % mainf
print(rmtex)
system(rmtex)
allelse = (rmcmd + "*.aux\n" +
   rmcmd +  "*.bbl\n" + 
   rmcmd +  "*.blg\n" +
   rmcmd +  "*.dvi\n" +
   rmcmd +  "*.lof\n" + 
   rmcmd +  "*.log\n" +
   rmcmd +  "*.lot\n" +
   rmcmd +  "*.toc")
print(allelse)
system(allelse)
# -------------------------------------------------------------------------------
# names of inputs and outputs
# -------------------------------------------------------------------------------
intxt = mainf + ".txt"
outxt = mainf + ".txt2"
outex = mainf + ".tex"
# ------------------------------------------------------------------------------
# the original and the new txt files
# ------------------------------------------------------------------------------
ftxt1 = open(intxt,'rt')
ftxt2 = open(outxt,'wt')
# ------------------------------------------------------------------------------
# reinstate \@ref with \ref for pdflatex
# ------------------------------------------------------------------------------
for line in ftxt1:
# -----------------------------------------------------------------------------
# skips indented code
# -----------------------------------------------------------------------------
   if line[0] == "\t" or line[0:4] == "    " :
      ftxt2.write(line)
      continue
   line = line.replace(r'\@ref',r'\ref')
   ftxt2.write(line)
ftxt2.close()
panstringtex = '''pandoc -V fontsize=12pt -V lang=%s --template=manuscript.latex \
--bibliography=%s   --csl=%s \
-N -S -s  -f markdown -t latex %s -o %s''' % (lang,bibf,cslf,outxt,outex)
print(panstringtex)
system(panstringtex)
# ------------------------------------------------------------------------------
# EXCLUSIVE for abnt.cls: open the tex, find the abnt glitches, fix them
# ------------------------------------------------------------------------------
if cslf == "abnt.csl":
   ftex = open(outex,'rt')
   content = ftex.read()
   ftex.close()
   result = re.findall(r', \([0-9]{4}\)',content)
   result = list(set(result))
   for me in result:
      content = content.replace(me,me[1:])
   ftex = open(outex,'wt')
   ftex.write(content)
   ftex.close()
# ------------------------------------------------------------------------------
# run pdflatex over and over to resolve cross-references
# ------------------------------------------------------------------------------
system("pdflatex %s" % mainf)
system("pdflatex %s" % mainf)
system("pdflatex %s" % mainf)
# ------------------------------------------------------------------------------
# now on to docx generation
#    start by deleting previous version
# ------------------------------------------------------------------------------
rmdocx = (rmcmd + " %s.docx") % mainf
print(rmdocx)
system(rmdocx)
rmodt = (rmcmd + " %s.odt") % mainf
print(rmodt)
system(rmodt)
# ------------------------------------------------------------------------------
# sadthing: search and replacement strings within a line are collected in
# the global variable searchrepl.
# ------------------------------------------------------------------------------
def sadthing(line):
   wherelist = [line.find("\\newlabel{eq:"),
                line.find("\\newlabel{fig:"),
                line.find("\\newlabel{sec:"),
                line.find("\\newlabel{subsec:"),
                line.find("\\newlabel{tab:")]
   wheres = [(index,value) for (index,value) in enumerate(wherelist) if value >= 0]
# ------------------------------------------------------------------------------
# at each line, only one of these instances, at most, can appear
# ------------------------------------------------------------------------------
   assert 0 <= len(wheres) <= 1
   if len(wheres) == 0:                # nothing in this line
      where = -1
   elif len(wheres) == 1:              # something in this line
      index = wheres[0][0]
      where = wheres[0][1]
   else:                               # tragedy struck
      print("something very wrong")
      exit(1)
   if where >= 0 :
# ------------------------------------------------------------------------------
# "what" refers to the label being searched
# ------------------------------------------------------------------------------
      search_in = line.find("\\newlabel{") + 10
      search_end = line.find("}")
# ------------------------------------------------------------------------------
# "where" refers to the number being replaced
# ------------------------------------------------------------------------------
      repl_in = line.find("}{{")+3
      repl_end = line.find("}",repl_in)
      asearch = "\\ref{"+line[search_in:search_end]+"}"
      arepl   = line[repl_in:repl_end]
      searchrepl.append((asearch,arepl))
   pass
pass
# ------------------------------------------------------------------------------
# read the aux file
# ------------------------------------------------------------------------------
auxf = mainf + ".aux"
aux = open(auxf,"rt")
# ------------------------------------------------------------------------------
# really thorny part: resolve cross-references
#    an empty string of replacements
# ------------------------------------------------------------------------------
searchrepl = []
for line in aux:
   sadthing(line)
pass
print(searchrepl)
# ------------------------------------------------------------------------------
# include section numbering
# ------------------------------------------------------------------------------
def secnum(line):
   aline = line.split()
   n = len(aline)
#   print(aline[n-1])
   insert = aline[n-1].replace(r'\label',r'\ref')
   line = aline[0] + " " + insert
   for k in range(1,n):
      line = line + " " + aline[k]
#   print('secnum: ',line)
   return(line)
# ------------------------------------------------------------------------------
# the original and the new txt files
# ------------------------------------------------------------------------------
ftxt1 = open(intxt,'rt')
ftxt2 = open(outxt,'wt')
# ------------------------------------------------------------------------------
# prepare to write the txt2 file
# ------------------------------------------------------------------------------
switchverb = False
for line in ftxt1:
   outline = line
# -----------------------------------------------------------------------------
# check for headers
# -----------------------------------------------------------------------------
   if outline[0:2] == "# " and "\\label{sec:" in outline and not(switchverb):
      outline = secnum(outline)
   if outline[0:3] == "## " and "\\label{subsec:" in outline and not(switchverb):
      outline = secnum(outline)
# -----------------------------------------------------------------------------
# skips indented code
# -----------------------------------------------------------------------------
   if outline[0] == "\t" or outline[0:4] == "    " :
      ftxt2.write(outline)
      continue
# -----------------------------------------------------------------------------
# skips fenced blocks
# -----------------------------------------------------------------------------
   if outline[0:3] == "~~~" or outline[0:3] == "```" :
      switchverb = not switchverb
   if switchverb :
      ftxt2.write(outline)
      continue
# ------------------------------------------------------------------------------
# replaces cross-references
# ------------------------------------------------------------------------------
   for (asearch,arepl) in searchrepl:
      outline = outline.replace(asearch,arepl)
   pass
# ------------------------------------------------------------------------------
# finally, reinstate \@ref with \ref
# ------------------------------------------------------------------------------
   outline = outline.replace(r'\@ref',r'\ref')
   ftxt2.write(outline)
pass   
# ------------------------------------------------------------------------------
# closes the textfiles neatly
# ------------------------------------------------------------------------------
ftxt1.close()
ftxt2.close()
# ------------------------------------------------------------------------------
# cleans the previously generated docx
# ------------------------------------------------------------------------------
outdocx = mainf + ".docx"
outodt  = mainf + ".odt"
# ------------------------------------------------------------------------------
# generates the docx
# ------------------------------------------------------------------------------
panstringdocx = '''pandoc --bibliography=%s  \
--csl=%s -N -S -s  -f markdown -t docx %s  -o %s''' % (bibf,cslf,outxt,outdocx)
print(panstringdocx)
system(panstringdocx)
panstringodt = '''pandoc --bibliography=%s  \
--csl=%s -N -S -s  -f markdown -t odt %s  -o %s''' % (bibf,cslf,outxt,outodt)
print(panstringodt)
system(panstringodt)
# ------------------------------------------------------------------------------
# cleans the temporary txt2 file
# ------------------------------------------------------------------------------
rmtxt2 = rmcmd + mainf + ".txt2"
print(rmtxt2)
system(rmtxt2)
