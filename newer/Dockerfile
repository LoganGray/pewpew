FROM node:latest
EXPOSE 8080
WORKDIR /app
RUN npm install http-server -g
CMD ["http-server", "-a", "0.0.0.0", "-p", "8080", "--cors", "-c-1", "/app"]

