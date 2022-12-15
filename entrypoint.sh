#!/bin/bash

# exit when any command fails
set -e

git config --global --add safe.directory /github/workspace
gh repo view
echo GITHUB_EVENT_NUMBER=$GITHUB_EVENT_NUMBER
gh api -H "Accept: application/vnd.github+json" /repos/swisschain/tmp-dc-tls/pulls
#- run: gh api -H "Accept: application/vnd.github+json" /repos/${{ github.repository_owner }}/${{ github.event.repository.name }}/pulls
