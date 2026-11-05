#!/bin/sh
# Finds Python 3.8 or later and runs one script of this plugin.
for py in python3 python py; do
  if "$py" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
    exec "$py" "$@"
  fi
done
echo "This plugin needs Python 3.8 or later, which was not found, so its check did not run." >&2
exit 0
