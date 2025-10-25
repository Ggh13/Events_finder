FROM golang:1.24.2 AS builder

WORKDIR /workflow

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 go build -o test ./...

FROM alpine:latest

WORKDIR /app

COPY --from=builder /workflow/test .

EXPOSE 8080

CMD ["./test"]