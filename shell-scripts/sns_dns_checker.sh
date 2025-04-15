#!/usr/bin/bash
if [ $# -eq 0 ];
then
  echo "$0: Missing Domain"
  exit 1
elif [ $# -gt 1 ];
then
  echo "$0: Too many arguments: $@"
  exit 1
else
  echo "==========================="
  echo "Domain entered...: $@"
  echo "Domain #1..............: $1"
fi
echo "Fetching required DNS value..."
echo ""
aws ses --region us-west-2 verify-domain-dkim --domain $1 | jq -r --arg domain $1 '.DkimTokens[] + "._domainkey." + $domain' > dns_name.txt
aws ses --region us-west-2 verify-domain-dkim --domain $1 | jq -r '.DkimTokens[] + ".dkim.amazonses.com"' > dns_value.txt
readarray -t dns_name < dns_name.txt
readarray -t dns_value < dns_value.txt
echo "Files created dns_name.txt && dns_value.txt"

for i in 0 1 2
do
  compare=$(dig cname ${dns_name[$i]} +short)
  echo "------------------------------------------------------------------------------------"
  echo "DOMAIN:| $1"
  echo "------------------------------------------------------------------------------------"
  if test "$compare" = "${dns_value[$i]}"
  then
  echo "DNS record valid:"
  echo "------------------------------------------------------------------------------------"
  echo -e "VALUE:| \033[32mbold${dns_name[$i]}\033[0m"
  echo "------------------------------------------------------------------------------------"
  elif test "$compare" = "${dns_value[$i]}."
  then
  echo "DNS record valid:"
  echo "------------------------------------------------------------------------------------"
  echo -e "VALUE:| \033[32mbold${dns_value[$i]}.\033[0m"
  echo "------------------------------------------------------------------------------------"  
  else
  echo -e "\033[31mERROR:| Incorrect DNS value detected:
      | $compare\033[0m"
  echo "------------------------------------------------------------------------------------"
  echo "Please update the DNS record with the following:"
  echo "------------------------------------------------------------------------------------"
  echo "NAME:| ${dns_name[$i]}"
  echo "------------------------------------------------------------------------------------"
  echo -e "VALUE:| \033[32m${dns_value[$i]}\033[0m"
  echo "------------------------------------------------------------------------------------"
  fi
echo ""
  if test $i -lt 1
  then
  echo "Checking next record"
  elif test $i -eq 1
  then
  echo "Checking last record"
  else
  echo "Checks completed"
  fi
done