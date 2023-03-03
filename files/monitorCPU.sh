#! /bin/bash
outfile="$1"
: > $outfile

while true; do
#MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%\t\t", $3*100/$2 }')
CPU=$(uptime | awk '{printf "%.2f\t\t\n", $(NF-2)}')
echo "$CPU" >> $outfile
sleep 60
done
