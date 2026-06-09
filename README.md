Ephemeral Chat App: Shifting From Stateless to Stateful on DOKS
This repository contains a real-time Python/Flask chat application deployed on DigitalOcean Kubernetes (DOKS) using Redis as a backend. The core focus of this project is to explicitly demonstrate and analyze the difference between a Stateless and Stateful architecture by running a controlled cluster disruption test.

🏗 Repository Structure
app.py – The Python Flask application using Redis Pub/Sub / Lists.

Dockerfile – Container configuration for the Flask app.

app.yaml – Kubernetes Deployment (2 replicas) and LoadBalancer Service for the web app.

redis.yaml – Kubernetes Deployment and ClusterIP Service for the Redis backend.

redis-pvc.yaml – Kubernetes PersistentVolumeClaim using do-block-storage.

🛠 Prerequisites
Before executing the manifests, ensure you have the following tools configured:

An active DigitalOcean Account with a provisioned Kubernetes (DOKS) cluster.

doctl CLI installed and authenticated.

kubectl CLI installed locally.

Docker Desktop running locally.

📥 Step 1: Cluster Context Connection
To avoid default localhost:8080 connection errors, link your local machine to your cloud cluster.

Find your DOKS cluster name:

Bash
doctl kubernetes cluster list
Save the cluster context (Execute as your regular local user):

Bash
doctl kubernetes cluster kubeconfig save <your-cluster-name>
(Note for Linux users using the doctl Snap: If you encounter sandbox permission errors, run sudo snap connect doctl:kube-config and mkdir -p $HOME/.kube before trying again).

Verify the active link:

Bash
kubectl get nodes
🧪 Step 2: Phase 1 — Testing the "Stateless" Behavior
In this phase, Redis stores data exclusively in volatile container memory (RAM). If the container dies, the data dies.

Apply the baseline manifests:

Bash
kubectl apply -f redis.yaml
kubectl apply -f app.yaml
Retrieve the Load Balancer IP:

Bash
kubectl get svc chat-app-lb -w
Once the EXTERNAL-IP resolves, copy and paste it into your web browser.

Run the Stateless Disruption Test:

Open the app in your browser and post 3 or 4 messages.

In your terminal, simulate an unexpected crash by deleting the Redis pod:

Bash
kubectl delete pod -l app=redis
Wait roughly 10 seconds for the pod to cycle, then refresh your browser.

Result: The chat history is completely gone.

💾 Step 3: Phase 2 — Shifting the Architecture to "Stateful"
To ensure our data layer survives container lifecycles, we transition to a stateful setup by connecting an external DigitalOcean Cloud SSD.

Provision the DigitalOcean Block Storage:

Bash
kubectl apply -f redis-pvc.yaml
Upgrade Redis to use the Volume Mounts:
Open your redis.yaml and ensure it includes the stateful refactoring configurations (the command: ["redis-server", "--appendonly", "yes"], volumeMounts, and pod volumes mapping to your redis-pvc). Then apply the changes:

Bash
kubectl apply -f redis.yaml
Kubernetes will perform a rolling update, detaching the old stateless configuration and mounting the new storage disk.

Run the Stateful Disruption Test:

Return to your browser app and post new messages (e.g., "This data lives on an SSD!").

Delete the Redis pod once more to simulate another failure:

Bash
kubectl delete pod -l app=redis
Watch the real-time file recovery metrics straight from your new pod logs:

Bash
kubectl get pods
kubectl logs <new-redis-pod-name>
(Look for: * DB loaded from append only file...)

Refresh your browser. * Result: Your messages remain perfectly intact! The cloud SSD was successfully re-attached to the new pod container.

🧹 Resource Cleanup
To stop DigitalOcean from billing you for the active Load Balancer and Block Storage assets when you are done experimenting, tear down all resources completely:

Bash
kubectl delete -f app.yaml
kubectl delete -f redis.yaml
kubectl delete -f redis-pvc.yaml
📊 Core Architecture Takeaways
Stateless Layer (app.yaml): Easily scales up or down horizontally. Pods can be destroyed without care because they don't retain data local to their filesystem.

Stateful Layer (redis.yaml + redis-pvc.yaml): Requires decoupled, cloud-managed block storage volumes to maintain state over container lifecycles. Data is persistent and survives pod terminations.
