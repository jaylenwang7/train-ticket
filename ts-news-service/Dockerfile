FROM golang:alpine3.19

RUN mkdir -p /app
WORKDIR /app

ADD . /app/
RUN go mod tidy & go build -o app
CMD [ "./app" ]