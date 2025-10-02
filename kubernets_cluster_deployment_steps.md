# Configure `kubectl` on Ubuntu Desktop to Access Kubernetes Cluster

This guide explains how to install and configure `kubectl` on your Ubuntu desktop so you can manage your Kubernetes cluster remotely.

---

## 1. Install kubectl on Ubuntu

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl

# Add Kubernetes signing key
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg \
  https://dl.k8s.io/apt/doc/apt-key.gpg

# Add Kubernetes repo
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] \
https://apt.kubernetes.io/ kubernetes-xenial main" | \
sudo tee /etc/apt/sources.list.d/kubernetes.list

# Install kubectl
sudo apt-get update
sudo apt-get install -y kubectl
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
