aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 004110525981.dkr.ecr.eu-west-2.amazonaws.com
docker build -t geocrypto-api-service .
docker tag geocrypto-api-service:latest 004110525981.dkr.ecr.eu-west-2.amazonaws.com/geocrypto-api-service:latest
docker push 004110525981.dkr.ecr.eu-west-2.amazonaws.com/geocrypto-api-service:latest