## IV. Cluster Bootstrap (Control-Plane Node Only)

***Note: Run this step ONLY on the Control-Plane (Master) node.***

* **Initialize the Cluster:** Replace `<POD-CIDR>` with your chosen Pod network range (e.g., `10.244.0.0/16` for Flannel).
    ```bash
    sudo kubeadm init --pod-network-cidr=<POD-CIDR>
    ```

* **Set up Kubeconfig for Root User:**
    ```bash
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    ```

* **Set up Kubeconfig for Non-Root User:** (If needed)
    ```bash
    mkdir -p /home/user/.kube
    sudo cp -i /etc/kubernetes/admin.conf /home/user/.kube/config
    sudo chown user:user /home/user/.kube/config
    ```

* **Apply CNI Network Plugin:** (Example shown for Calico)
    ```bash
    kubectl apply -f [https://docs.tigera.io/calico/latest/manifests/calico.yaml](https://docs.tigera.io/calico/latest/manifests/calico.yaml)
    ```

* **Generate Join Command:** Save the output of this command, as it's needed for worker nodes.
    ```bash
    kubeadm token create --print-join-command
    ```

---

## V. Join Worker Nodes

***Note: Run this step ONLY on the Worker Nodes.***

* **Join the cluster:** Use the token and command generated in the previous step.
    ```bash
    sudo kubeadm join <Control-Plane-IP>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
    ```

---

## VI. Remote Management Tool Setup & Access (Desktop/Management Machine)

These steps are for your dedicated Ubuntu desktop to manage the cluster remotely.

* **Copy `kubeconfig` from Control-Plane Node:**
    ```bash
    scp user@<master-node-ip>:/etc/kubernetes/admin.conf ~/kubeconfig
    ```

* **Configure `kubeconfig` on Desktop:**
    ```bash
    mkdir -p ~/.kube
    cp ~/kubeconfig ~/.kube/config
    chmod 600 ~/.kube/config
    ```

* **Test the Connection:**
    ```bash
    kubectl get nodes
    ```

---

## VII. Application Configuration and Deployment

These steps configure the network load balancer and deploy your specific applications.

### A. Node Labeling

Label your specific worker nodes as required by the deployments (`k8s-w1` for app1, `k8s-w2` for app2).

```bash
kubectl label node k8s-w1 role=app1
kubectl label node k8s-w2 role=app2
kubectl get nodes --show-labels
```
## Install and Configure MetalLB (LoadBalancer)

```bash
kubectl apply -f [https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb.yaml](https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb.yaml)
```

## Configure IP Address Pool: Apply your custom configuration using the provided file. The range is 192.168.0.51-192.168.0.55.
````bash
# Apply the MetalLB configuration file (metallb-custom.yaml)
kubectl apply -f metallb-custom.yaml
----
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

## Install NGINX Ingress Controller
````bash
kubectl apply -f [https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml](https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml)
````

## Verify LoadBalancer IP: Wait for the EXTERNAL-IP to be assigned by MetalLB.
````bash
kubectl get svc -n ingress-nginx
````

##  Deploy Applications and Ingress Rules
````bash
# Apply the main application deployment manifest
kubectl apply -f app_deployments.yaml
````

VIII. Final Access Check
Update Local Hosts File: On your desktop, edit your local /etc/hosts file (or equivalent) to direct traffic for the hostnames to the NGINX Ingress Controller's External IP (the one assigned by MetalLB).

# Kubernetes Ingress mapping
<EXTERNAL-IP>   app1.myk8s.com
<EXTERNAL-IP>   app2.myk8s.com
Access the Applications: You can now access your applications using the hostnames in a web browser.