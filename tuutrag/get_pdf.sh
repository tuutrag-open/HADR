#!/bin/bash
# Downloads PDFs, storing them in PDF folder
for i in $(seq 1 40);
do
        link=$(jq -r --arg key "$i" '.[$key]["Link:"]' ../data/meta/magentabook_meta.json)
        name=$(jq -r --arg key "$i" '.[$key]["PDF Name:"]' ../data/meta/magentabook_meta.json)
        name="${name//[. ]/_}"
        name="${name//_pdf/}"
        curl "$link" -o "../data/ccsds/magenta/${name}.pdf"
done

for i in $(seq 1 99);
do
        link=$(jq -r --arg key "$i" '.[$key]["Link:"]' ../data/meta/bluebook_meta.json)
        name=$(jq -r --arg key "$i" '.[$key]["PDF Name:"]' ../data/meta/bluebook_meta.json)
        name="${name//[. ]/_}"
        name="${name//_pdf/}"
        curl "$link" -o "../data/ccsds/blue/${name}.pdf"
done

