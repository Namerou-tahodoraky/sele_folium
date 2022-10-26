#!/bin/bash
docker run --rm --name sele -p 4444:4444 -p 5900:5900 -v /home/wsl/study/selenium/html:/share selenium/standalone-chrome:4.1.4-20220427
