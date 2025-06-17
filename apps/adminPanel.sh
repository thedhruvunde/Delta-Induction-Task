#!/bin/bash
AUTHOR_ROOT="/home/authors"
#Admin only check
if ! id -nG "$USER" | grep -qw "g_admin"; then
  echo "Only admins can run this script."
  exit 1
fi
