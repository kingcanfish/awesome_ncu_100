sh docker build . -f Dockerfile -t ncu100 &&
docker run -d --restart=always --name ncu_100 -v $(pwd):/code ncu100:latest
