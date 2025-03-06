# Path Finder

### Why I Made This Project
Ever since I was young I've always wondered why google maps works. Or more straightforward, "How does the app know, how to get from point a to point b?" Its a question that plagued me for a long time. Fortunately, I finally got my answer in my Artifical Intelligence class 

### How to Run My Program
All you will need to run my program is to have Docker installed. If you do not already have it installed below is an installion link:

https://www.docker.com/products/docker-desktop/

Docker allows you to run my program without any extra installation. All you have to do is open the command prompt or shell and run these following commands

**Docker pull tylerkelly1/pffrontend:latest**

**Docker pull tylerkelly1/pfbackend:latest**

**Docker run -d -p 80:80 tylerkelly1/pffrontend:latest**

**Docker run -d -p 8000:8000 tylerkelly1/pfbackend:latest**

Sure enough it is as simple as that. Now to use the application just goto:

http://localhost

This will take you to the local host on which your local docker container is now running!



## Tech Stack

**Client:** CSS, TypeScript/JavaScript, HTML

**Server:** Python, FastAPI, pydantic

**Deployment:** Docker, Docker Hub

