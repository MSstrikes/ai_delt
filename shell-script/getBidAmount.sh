#!/bin/bash

args=''
for i in `seq 2 $#`
do
    args=$args' '${!i}
done
exec_str='node query-adset-bid.js '$1' '$args
cd nodejs/script
eval $exec_str
