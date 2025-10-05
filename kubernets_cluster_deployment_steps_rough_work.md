# Configure `kubectl` on Ubuntu Desktop to Access Kubernetes Cluster

This guide explains how to install and configure `kubectl` on your Ubuntu desktop so you can manage your Kubernetes cluster remotely.

---

## 1. Install kubectl on Ubuntu

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl

ARCH=$(dpkg --print-architecture)

# Download the latest stable kubectl release for your architecture
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/${ARCH}/kubectl"

# Make the downloaded binary executable
chmod +x kubectl

# Move the kubectl binary to a directory in your PATH (e.g., /usr/local/bin)
sudo mv kubectl /usr/local/bin/kubectl
```

Verify installation:

```bash
kubectl version --client
```

---

## 2. Get kubeconfig from Cluster Node

On your **Kubernetes master (control plane)** node, kubeconfig is usually located at:

```
/etc/kubernetes/admin.conf
```

Copy it to your desktop using `scp`:

```bash
scp user@<master-node-ip>:/etc/kubernetes/admin.conf ~/kubeconfig
```

---

## 3. Configure kubeconfig on Desktop

On your desktop:

```bash
mkdir -p ~/.kube
cp ~/kubeconfig ~/.kube/config
chmod 600 ~/.kube/config
```

---

## 4. Test the Connection

```bash
kubectl get nodes
```

Expected: List of your cluster nodes (master + workers).

---

## 5. Notes for VirtualBox (Bridge Networking)

* Since your cluster VMs use **bridge networking**, they get LAN IPs from your router (e.g., `192.168.x.x`).
* Ensure:

  * You can **SSH** into the master node from your desktop.
  * Port **6443** (Kubernetes API server) is reachable.

Check with:

```bash
telnet <master-node-ip> 6443
```

---

## ✅ Summary

1. Install `kubectl` on Ubuntu.
2. Copy `/etc/kubernetes/admin.conf` from master.
3. Save as `~/.kube/config`.
4. Test with `kubectl get nodes`.

You’re now ready to manage your Kubernetes cluster from your Ubuntu desktop!


# Configuring the kubernets cluster with app deployment
This is step by step guide to app deployments

## Creating/Giving levels for nodes
```bash
  kubectl label nodes k8s-w1 role=app1
  kubectl label nodes k8s-w2 role=app2

```

# Kubernetes Installation
## Prepare the Worker Node (This is mainly for Ubuntu)

````bash
### Update system
sudo apt update && sudo apt upgrade -y

# Disable swap (K8s requires swap OFF)
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# Load required kernel modules
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

# Set sysctl params required by Kubernetes
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system
```

## Install Container Runtime (Containerd recommended)
````bash
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker repo (for containerd)
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y containerd.io

# Configure containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml

# Use systemd as cgroup driver
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

# Restart
sudo systemctl restart containerd
sudo systemctl enable containerd


sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key

echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] \
https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" | \
sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

````

### 3. Install kubeadm, kubelet, kubectl
````bash
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

````

## Initiate Control Plane
# [Great Conversation For Pod Networking](https://chatgpt.com/c/68e0c1e0-cc98-8323-94cf-bc25aa964111)
# For Calico sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --service-cidr=10.96.0.0/12


# For Weave sudo kubeadm init --pod-network-cidr=10.32.0.0/12 --apiserver-advertise-address=192.168.0.161
                  +----------Kubernetes Cluster - Weave Networking----------------+
                  |                                                               |
   Node 1 (Worker)| Pod CIDR: 10.32.0.0/24   Pod IPs: 10.32.0.2, 10.32.0.3 ...    |
                  |   +--------+     +--------+                                   |
                  |   |  Pod A |     |  Pod B |                                   |
                  |   |10.32.0.2|    |10.32.0.3|                                  |
                  |   +--------+     +--------+                                   |
                  |                                                               |
   Node 2 (Worker)| Pod CIDR: 10.33.0.0/24   Pod IPs: 10.33.0.2, 10.33.0.3 ...    |
                  |   +--------+     +--------+                                   |
                  |   |  Pod C |     |  Pod D |                                   |
                  |   |10.33.0.2|    |10.33.0.3|                                  |
                  |   +--------+     +--------+                                   |
                  |                                                               |
   Node 3 (Worker)| Pod CIDR: 10.34.0.0/24   Pod IPs: 10.34.0.2, 10.34.0.3 ...    |
                  |   +--------+     +--------+                                   |
                  |   |  Pod E |     |  Pod F |                                   |
                  |   |10.34.0.2|    |10.34.0.3|                                  |
                  |   +--------+     +--------+                                   |
                  |                                                               |
                  +----------------------------------------------------------------+



## Comment If you are changing the --pod-network-cidr=<Custom Range> then while implementing CNI you need to define or mention during CNI implementation 

## For Weave - kubectl apply -f "https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml"
## For Calico - kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
#### For custom pod-network define environmental variable - IPALLOC_RANGE

sudo kubeadm token create --print-join-command #### Command to join Cluster

## How to add Node to K*S cluster 
# sudo kubeadm join 192.168.0.161:6443 --token SOME_TOKEN  --discovery-token-ca-cert-hash sha256:SOME_TOKEN

## How to Remove the Node from cluster -- Start
##### ON Control Plane
kubectl cordon <node-name>
kubectl drain <node-name> --ignore-daemonsets --delete-empty-dir-data
##### On Node Worker
sudo kubeadm reset
# Clean up networking configurations (optional but recommended)
sudo rm -rf /etc/cni/net.d
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X
##### On Node Worker
kubectl delete node <node-name>
## How to Remove the Node from cluster -- End


##### RESET THE ENTIRE CLUSTER OF K8S START
sudo kubeadm reset -f
# Remove the Kubernetes configuration directory
sudo rm -rf /etc/kubernetes

# Remove the etcd data directory
sudo rm -rf /var/lib/etcd

# Remove the kubelet configuration and data
sudo rm -rf /var/lib/kubelet
# Clear CNI network configurations
sudo rm -rf /etc/cni/net.d

# Flush all IP tables (clears any rules set by kube-proxy or the CNI)
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X

sudo systemctl daemon-reload
sudo systemctl restart kubelet

##### RESET THE ENTIRE CLUSTER OF K8S END


## Installing Ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/baremetal/deploy.yaml

## Deploy metalLB (Inhouse demo Load Balancer)
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml

````bash
# metalb-custom.yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: default-address-pool
spec:
  addresses:
  - 192.168.0.51-192.168.0.55   # free IPs from your LAN

---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  namespace: metallb-system
  name: default
````
kubectl apply -f metalb-custom.yaml


## Ingress Resources yaml file
````bash
ingress-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  type: LoadBalancer
  ports:
    - name: http
      port: 80
      targetPort: http
    - name: https
      port: 443
      targetPort: https
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/component: controller

````

## Ingress resource config
````bash
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: apps-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: app1.myk8s.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app1-service
            port:
              number: 80
  - host: app2.myk8s.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app2-service
            port:
              number: 80
````