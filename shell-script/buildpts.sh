#!/bin/bash

exec_str='node build-pts.js '$1''
cd nodejs/script
eval $exec_str
