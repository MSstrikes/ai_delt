#!/bin/bash

args=''
for i in `seq 2 $#`
do
    args=$args' '${!i}
done
exec_str='node scripts/query-ad-status.js '$1' '$args
cd /Users/youhaolin/ai_adt
eval $exec_str
