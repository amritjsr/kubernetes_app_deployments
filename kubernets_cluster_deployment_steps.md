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
# sudo kubeadm init --pod-network-cidr=10.32.0.0/12

sudo kubeadm init --pod-network-cidr=10.32.0.0/12 --apiserver-advertise-address=192.168.0.161

kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')"

sudo kubeadm token create --print-join-command #### Command to join Cluster


