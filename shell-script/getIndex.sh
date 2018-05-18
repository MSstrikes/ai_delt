#!/bin/bash

i=1
args=''
for var in "$@"
do
    if [ $i -ne 1 ] ; then
       args=$args' '$var
    fi

    if [ $i -eq 1 ] ; then
       i=0
    fi
done
exec_str='node query-many-insights.js '$1' '$args
cd nodejs/script
eval $exec_str
