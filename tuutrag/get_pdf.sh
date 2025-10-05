#!/bin/bash
# Downloads PDFs, storing them in PDF folder
for i in $(seq 1 40);
do
        link=$(jq -r --arg key "$i" '.[$key]["Link:"]' Magenta_metadata.json)
        name=$(jq -r --arg key "$i" '.[$key]["PDF Name:"]' Magenta_metadata.json)
        name="${name//[. ]/_}"
        name="${name//_pdf/}"
        curl "$link" -o "../data/scraped/magenta_books/${name}.pdf"
done

for i in $(seq 1 99);
do
        link=$(jq -r --arg key "$i" '.[$key]["Link:"]' Blue_metadata.json)
        name=$(jq -r --arg key "$i" '.[$key]["PDF Name:"]' Blue_metadata.json)
        name="${name//[. ]/_}"
        name="${name//_pdf/}"
        curl "$link" -o "../data/scraped/blue_books/${name}.pdf"
done

