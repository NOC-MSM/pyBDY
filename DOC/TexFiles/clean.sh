rm -f $( ls -1 pyBDY.* | egrep -v "(tex|pdf)" ) *mpgraph*
rm -f Chapters/*.aux Chapters/*.log
rm *.idx *.log *.maf *.mtc* *.out *.pdf *.gz *.toc *.aux
