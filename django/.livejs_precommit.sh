#!/usr/bin/bash

# Script to comment out LiveJs reload script

if [[ "$(uname)" == "Darwin" ]]; then
  # Mac
   bash -c "find . -type f -name 'base.html' | xargs sed -ri '' 's/^(\s)*[^\{]+(<script.*livejs.*script>)/\1\{\# \2 \#\}/' "
else
   bash -c "find . -type f -name 'base.html' | xargs sed -ri 's/^(\s)*[^\{]+(<script.*livejs.*script>)/\1\{\# \2 \#\}/' "

fi
