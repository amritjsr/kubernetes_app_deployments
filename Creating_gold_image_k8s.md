# Kubernetes Cluster Setup and Management Guide

This document organizes the steps for preparing nodes, installing core components, setting up remote management, and performing post-deployment configuration for a Kubernetes cluster.

---

## I. Prepare the Worker Node (Prerequisites)

These are foundational system-level configurations required on an Ubuntu worker node before it can join the Kubernetes cluster.

* **Update system and disable swap:** Kubernetes requires swap to be disabled.
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo swapoff -a
    sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
    ```

* **Load required kernel modules (`overlay`, `br_netfilter`):**
    ```bash
    cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
    overlay
    br_netfilter
    EOF
    sudo modprobe overlay
    sudo modprobe br_netfilter
    ```

* **Set sysctl parameters for Kubernetes networking:** This ensures required network settings for Kubernetes networking components.
    ```bash
    cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
    net.bridge.bridge-nf-call-iptables  = 1
    net.bridge.bridge-nf-call-ip6tables = 1
    net.ipv4.ip_forward                 = 1
    EOF

    sudo sysctl --system
    ```

---

## II. Install Container Runtime (containerd)

Containerd is the open-source container runtime used by Kubernetes.

* **Install required packages:**
    ```bash
    sudo apt-get update && sudo apt-get install -y \
      apt-transport-https ca-certificates curl gnupg lsb-release
    ```

* **Add Docker's official GPG key:**
    ```bash
    curl -fsSL [https://download.docker.com/linux/ubuntu/gpg](https://download.docker.com/linux/ubuntu/gpg) | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    ```

* **Set up the stable repository:**
    ```bash
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] [https://download.docker.com/linux/ubuntu](https://download.docker.com/linux/ubuntu) \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

* **Install containerd:**
    ```bash
    sudo apt-get update
    sudo apt-get install -y containerd.io
    ```

* **Configure containerd for Kubernetes and restart:**
    ```bash
    sudo mkdir -p /etc/containerd
    sudo containerd config default | sudo tee /etc/containerd/config.toml
    
    # Change SystemdCgroup to true (required for kubelet)
    sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
    
    sudo systemctl restart containerd
    sudo systemctl enable containerd
    ```

---

## III. Install Kubernetes Components (`kubeadm`*(Optional)*, `kubelet`, `kubectl`)

These are the primary Kubernetes tools: `kubeadm` (for cluster bootstrapping), `kubelet` (the node agent), and `kubectl` (the CLI management tool).

* **Add Kubernetes GPG Key and repository:**
    ```bash
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl
    
    curl -fsSL [https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key](https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key) | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] [https://pkgs.k8s.io/core:/stable:/v1.28/deb/](https://pkgs.k8s.io/core:/stable:/v1.28/deb/) /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
    ```

* **Install the components and hold their versions:**
    ```bash
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
    ```

---

## IV. Remote Management Tool Setup (`kubectl` on Desktop)

This phase covers installing and configuring the `kubectl` tool on your Ubuntu desktop to manage the cluster remotely. *Note: This installation assumes a separate machine from the cluster nodes.*

* **Install `kubectl` on Ubuntu Desktop:**
    ```bash
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl

    ARCH=$(dpkg --print-architecture)

    # Download the latest stable kubectl release for your architecture
    curl -LO "[https://dl.k8s.io/release/$(curl](https://dl.k8s.io/release/$(curl) -L -s [https://dl.k8s.io/release/stable.txt)/bin/linux/$](https://dl.k8s.io/release/stable.txt)/bin/linux/$){ARCH}/kubectl"

    # Make the downloaded binary executable and move it to a PATH directory
    chmod +x kubectl
    sudo mv kubectl /usr/local/bin/kubectl
    ```

* **Verify installation:**
    ```bash
    kubectl version --client
    ```

---

## V. Remote Access Configuration (on Desktop)

This phase details configuring the secure connection to the cluster's API server using the **kubeconfig** file.

* **Get `kubeconfig` from Cluster Master Node:** The configuration is usually at `/etc/kubernetes/admin.conf` on the master node.
    ```bash
    scp user@<master-node-ip>:/etc/kubernetes/admin.conf ~/kubeconfig
    ```

* **Configure `kubeconfig` on Desktop:**
    ```bash
    mkdir -p ~/.kube
    cp ~/kubeconfig ~/.kube/config
    chmod 600 ~/.kube/config
    ```

* **Test the Connection and API Server Reachability:**
    *Test Connection:* You should see a list of your cluster nodes (master + workers).
    ```bash
    kubectl get nodes
    ```

    *Network Check (especially for bridge networking setups):* Port **6443** (Kubernetes API server) must be reachable.
    ```bash
    telnet <master-node-ip> 6443
    ```

---