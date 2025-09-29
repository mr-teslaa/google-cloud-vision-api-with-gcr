docker build -t flexboneai-cloudvisionapi .


docker run -p 5000:8080 --env-file .env -v O:\Projects\flexbone-ai-assignement-cloudvisionapi\useful-variety-472007-c0-87c2d9af3842.json:/app/useful-variety-472007-c0-87c2d9af3842.json flexboneai-cloudvisionapi



gcloud run deploy flexbone-api --image=us-west2-docker.pkg.dev/YOUR_PROJECT_ID/images/google-cloud-vision-api-with-gcr:latest --platform=managed --region=us-west2 --allow-unauthenticated 