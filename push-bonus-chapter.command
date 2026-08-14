#!/bin/bash
cd "$(dirname "$0")"
git push
echo ""
echo "Done. Press any key to close."
read -n 1
