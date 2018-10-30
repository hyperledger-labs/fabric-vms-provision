#!/bin/bash

set -x

git checkout -- roles/common/files/hosts
git checkout -- roles/create/tasks/main.yml

rm autogen*
rm hosts
rm log*
