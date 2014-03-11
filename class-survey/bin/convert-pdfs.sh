#! /bin/bash

paths=`ls ../plots/2014/*.pdf`


for f in $paths
do
    n=${f/\.pdf/\.jpg}
    convert -density 300 -compress jpeg -quality 100 $f $n
done

