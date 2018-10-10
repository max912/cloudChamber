#!/bin/bash

t=$(($1*1000))

raspistill -f -t $t
