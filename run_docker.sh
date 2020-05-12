#!/bin/bash

docker run --rm -it -v "${PWD}":/home \
                    --device /dev/snd \
                    --name jumpcutter \
                    jumpcutter bash

