docker build -t flexboneai-cloudvisionapi .


docker run -p 5000:8080 --env-file .env -v O:\Projects\flexbone-ai-assignement-cloudvisionapi\useful-variety-472007-c0-87c2d9af3842.json:/app/useful-variety-472007-c0-87c2d9af3842.json flexboneai-cloudvisionapi