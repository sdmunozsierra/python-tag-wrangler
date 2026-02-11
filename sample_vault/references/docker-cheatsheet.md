---
title: Docker Cheatsheet
tags:
  - reference
  - docker
  - devops
  - cheatsheet
---

# Docker Cheatsheet

## Common commands
```bash
docker build -t myapp .
docker run -p 8080:80 myapp
docker compose up -d
```

## Dockerfile best practices
- Use multi-stage builds
- Pin base image versions
- Minimize layers

#reference #docker #devops
