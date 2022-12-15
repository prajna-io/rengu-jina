#!/bin/sh
#

SIZE=$( rengu info | awk '( NR==3 ) { print $2 }' | cut -d= -f2 )

echo ${SIZE} 

rengu show -ojson '*' \
  | jq -scr 'sort_by(.ID) | .[]' \
  | tqdm --total=${SIZE} \
  | gzip > all.jl.gz
