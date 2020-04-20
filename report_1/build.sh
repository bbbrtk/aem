#!/usr/bin/env bash

infile="lab1.tex"
pdflatex ${infile} && pdflatex ${infile}

rm *log *out *aux