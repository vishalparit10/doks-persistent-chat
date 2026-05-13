Ephemeral Chat App on DigitalOcean Kubernetes (DOKS)
A real-time chat application built with Python (Flask) and Redis, demonstrating how to handle stateful workloads in Kubernetes using DigitalOcean Block Storage.

🚀 Overview
This project showcases a high-availability deployment on Kubernetes. While the web frontend is stateless and scales easily, the Redis backend is "stateful," utilizing a Persistent Volume Claim (PVC) to ensure chat history survives pod restarts or cluster updates.

Key Features
Persistence: Uses do-block-storage to persist Redis data.

High Availability: Scalable Flask frontend managed by a Load Balancer.

Containerized: Fully Dockerized and ready for CI/CD.

🛠️ Prerequisites
Before running this project, ensure you have:

A DigitalOcean account.

doctl (DigitalOcean CLI) installed and authenticated.

kubectl installed.

Docker installed locally.

📂 Project Structure

.
├── app.py              # Flask Application logic

├── Dockerfile          # Container definition

├── app.yaml            # K8s Deployment & LoadBalancer Service

├── redis.yaml          # K8s Redis Deployment & Internal Service

└── redis-pvc.yaml      # Persistent Volume Claim for DO Block Storage


🏗️ Step-by-Step Execution

1. Connect to your DOKS Cluster
First, point your local kubectl to your DigitalOcean cluster:

# Get your cluster name
doctl kubernetes cluster list

# Save the kubeconfig (replace <cluster-name> with yours)
doctl kubernetes cluster kubeconfig save <cluster-name>

# Verify connection
kubectl get nodes

2. Prepare the Container Registry
You need a place to store your app image. Replace <your-registry> with your DigitalOcean Container Registry name.

# Log in
doctl registry login

# Build the image
docker build -t registry.digitalocean.com/<your-registry>/chat-app:v1 .

# Push to DO
docker push registry.digitalocean.com/<your-registry>/chat-app:v1

3. Deploy the Infrastructure
Apply the manifests in the following order:

A. Storage Layer
kubectl apply -f redis-pvc.yaml

B. Database Layer
kubectl apply -f redis.yaml

C. Application Layer
Note: Ensure you update the image path in app.yaml to match your registry.
kubectl apply -f app.yaml

🔍 Verification & Testing

Get the Access URL
DigitalOcean will provision an External Load Balancer. This may take 2-3 minutes:

kubectl get svc chat-app-lb
Copy the EXTERNAL-IP and paste it into your browser.

The Persistence Test
To verify that the Persistent Volume is working:

Open the app and send a few messages.

Delete the Redis pod manually:
kubectl delete pod -l app=redis
Wait for a new pod to start, then refresh the browser. Your messages will still be there.

🧹 Cleanup

To avoid ongoing charges for the Load Balancer and Block Storage, delete the resources:

kubectl delete -f app.yaml
kubectl delete -f redis.yaml
kubectl delete -f redis-pvc.yaml

📝 License

Distributed under the MIT License. See LICENSE for more information.
