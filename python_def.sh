#!/bin/bash

file="grammar"
cat $file | grep -v "^$" > "temp.txt"

file="temp.txt"
output="cpp_script_yacc.py"
non_terminal=""
comment=false
while IFS= read -r line
do
    i=0
    for word in "$line"; do
      word="$(echo -e "${word}" | sed -e 's/^[[:space:]]*//')"

      if [[ ( ${word:0:1} == "/" ) || ( ${word:0:1} == "*" ) ]]; then
        echo -e "# $line" >> $output
        comment=true
        break
      fi

      if [[ ${word: -1} == ":" ]]; then
        non_terminal=${word::-1}
        if [[ $i -eq 0 ]]; then
          echo -e "def p_${word::-1}(p):" >> $output
        else
          echo -e "def p_${word::-1}$i(p):" >> $output
        fi
        comment=false
        break
      fi

      if [[ ${word:0:1} == "|" ]]; then
        if $comment ; then
          echo -e "\t\"\"\"$non_terminal : ${word:1}" >> $output
          comment=false
        else
          echo -e "\t\t\t\t\t\t${word}" >> $output
        fi
        non_terminal=""
        break
      fi

      if [[ ${word:0:1} == ";" ]]; then
        echo -e "\t\t\t\t\t\t\"\"\"" >> $output
        echo -e "\tpass" >> $output
        echo -e "\n" >> $output
        non_terminal=""
        comment=false
        break
      fi

      echo -e "\t\"\"\"$non_terminal : $word" >> $output
      comment=false

    done

done <"$file"

rm temp.txt
