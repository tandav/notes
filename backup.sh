#!/bin/bash -x

# Ensure script stops when commands fail.
set -e

fname="$pj/notes/backups/$(date -u +%Y-%m-%dT%H:%M:%SZ).db"
sqlite3 "$pj/notes/test.db" ".backup ${fname}"
gzip $fname
