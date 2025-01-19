#!/bin/bash
docker build -f Dockerfile-dev -t pewpew-dev .
docker run -p 8080:8080 -v $(pwd):/opt/pewpew pewpew-dev
