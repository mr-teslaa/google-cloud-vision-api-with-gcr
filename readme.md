
docker build --build-arg GOOGLE_CREDENTIALS_JSON="$(cat ./service.json)" --no-cache -t flexboneai-cloudvisionapi .


docker run -p 5000:8080 -v O:\Projects\flexbone-ai-assignement-cloudvisionapi\service.json:/app/service.json flexboneai-cloudvisionapi


gcloud run deploy google-cloud-vision-api-with-gcr --image=us-west2-docker.pkg.dev/useful-variety-472007-c0/images/google-cloud-vision-api-with-gcr:latest --platform=managed --region=us-central1 --allow-unauthenticated 