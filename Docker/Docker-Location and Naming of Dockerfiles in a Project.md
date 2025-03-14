
---
# Docker
Docker is a containerization protocol for building lightweight services which can all run in parallel on the same computer:
Key Benefits:
- Lightweight and spin-up quickly
- Packages up dependencies for each micro-service
- Easy to share across hardware and machine types.

## Key Documentation
- [Docker Manuals](https://docs.docker.com/manuals/)
- [Docker References](https://docs.docker.com/reference/)
- [Dockerfile Syntax Reference](https://docs.docker.com/reference/dockerfile/#overview)
- [Docker Build Github Actuins](https://docs.docker.com/build/ci/github-actions/)

### Location and Naming of Dockerfiles in a Project
#### **Location**

1. **Root of the Project**: The most common and recommended location for a `Dockerfile` is in the root directory of your project. This allows for straightforward builds without additional configuration[^1][^2][^4].
2. **Dedicated Subdirectories**: For projects with multiple services or Dockerfiles, it's common to place them in dedicated subdirectories (e.g., `docker/backend/Dockerfile` and `docker/frontend/Dockerfile`). This helps maintain a clean structure when dealing with multiple containers[^2][^6].
3. **Custom Folder**: Some developers use a dedicated folder like `.docker` in the root directory to store Docker-related files, including `Dockerfile`, `docker-compose.yml`, `.env`, and `.dockerignore`[^1][^6].

#### **Naming**

1. **Default Name**: The default name for a Dockerfile is simply `Dockerfile` (without an extension). Using this name allows Docker to automatically detect and use it during builds[^4][^7].
2. **Custom Names**: For projects requiring multiple Dockerfiles, custom naming conventions like `<purpose>.Dockerfile` (e.g., `backend.Dockerfile`, `frontend.Dockerfile`) are commonly used. This helps differentiate files based on their purpose[^4][^6][^8].
3. **File Extensions**: While the default is extensionless, some developers use `.dockerfile` as an extension for clarity or syntax highlighting in certain IDEs (e.g., `backend.dockerfile`). However, this requires specifying the file explicitly using the `-f` flag during builds (e.g., `docker build -f backend.dockerfile .`)[^3][^8].

#### **Best Practices**

- Use the default name (`Dockerfile`) for simplicity if there’s only one Dockerfile in the project.
- For multi-service projects, organize Dockerfiles into subdirectories or use descriptive names to avoid confusion.
- Ensure that the build context includes all necessary files by placing the Dockerfile appropriately relative to your source code[^5][^6].
