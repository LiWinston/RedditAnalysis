# Migration of Elasticsearch and Kibana from Helm to ECK Operator (v9.0.1)

**Objective:** To upgrade and transition our Elasticsearch and Kibana deployment from an older Helm-based installation (originally v8.5.1) to a modern, Elastic Cloud on Kubernetes (ECK) Operator-managed setup running Elasticsearch and Kibana version 9.0.1. A key requirement was to ensure compatibility with existing `kubectl port-forward` commands.

**Executive Summary:**
The existing Helm-managed Elasticsearch and Kibana deployment, along with its persistent data, was decommissioned. A new, fresh deployment of Elasticsearch 9.0.1 and Kibana 9.0.1 was provisioned using the ECK Operator in the `elastic` namespace. To maintain compatibility with established development practices, custom Kubernetes services (`elasticsearch-master` and `kibana-kibana`) were created to alias the new ECK-managed services, allowing original `kubectl port-forward` commands to function without modification.

---

## 1. Pre-Migration: Decommissioning Old Deployment

Given the decision **not to migrate existing data**, the first phase involved the complete removal of the old Helm-based deployment:

1.  **Uninstall Kibana Helm Release:**
    ```bash
    helm uninstall kibana -n elastic
    ```
    Associated Kibana pods and services were verified to be terminated.

2.  **Uninstall Elasticsearch Helm Release:**
    ```bash
    helm uninstall elasticsearch -n elastic
    ```
    Associated Elasticsearch pods (StatefulSet) and services were verified to be terminated.

3.  **Delete PersistentVolumeClaims (PVCs):**
    The PVCs used by the old Elasticsearch deployment were identified and manually deleted to free up storage resources.
    ```bash
    # Example commands (actual names were verified before deletion)
    # kubectl delete pvc <old-es-pvc-name-0> -n elastic
    # kubectl delete pvc <old-es-pvc-name-1> -n elastic
    ```
    Verification was performed to ensure all related pods, services, and PVCs were removed from the `elastic` namespace.

---

## 2. ECK Operator Setup

1.  **Install/Verify ECK Operator:**
    The Elastic Cloud on Kubernetes (ECK) Operator was installed (or verified to be running) in the `elastic-system` namespace using the official Elastic Helm chart.
    ```bash
    helm repo add elastic [https://helm.elastic.co](https://helm.elastic.co)
    helm repo update
    helm install elastic-operator elastic/eck-operator \
      --namespace elastic-system \
      --create-namespace
    ```
    The operator's readiness was confirmed by checking its pod status.

---

## 3. Deployment of New ECK-Managed Stack (v9.0.1)

All new resources were deployed in the `elastic` namespace.

### 3.1. Elasticsearch 9.0.1 Deployment

1.  **Define Elasticsearch Custom Resource (CR):**
    An `Elasticsearch` CRD (e.g., `elasticsearch-eck.yaml`) was created to define the new cluster:
    * `metadata.name`: `es-cluster-eck-v901` (example name for the ECK-managed cluster)
    * `metadata.namespace`: `elastic`
    * `spec.version`: `"9.0.1"`
    * `spec.nodeSets`: Configured with `count: 2` to match the previous node count.
    * `spec.nodeSets[].volumeClaimTemplates`:
        * `storage: "100Gi"`
        * `storageClassName: "perfretain"` (matching the previous storage configuration)

2.  **Apply Elasticsearch CR:**
    ```bash
    kubectl apply -f elasticsearch-eck.yaml
    ```
    The deployment and readiness of the Elasticsearch pods were monitored.

3.  **Retrieve `elastic` User Password:**
    The auto-generated password for the `elastic` superuser was retrieved from the Kubernetes secret created by ECK:
    ```bash
    kubectl get secret es-cluster-eck-v901-es-elastic-user -n elastic -o=jsonpath='{.data.elastic}' | base64 --decode; echo
    ```

4.  **Create Alias Service for Elasticsearch (`elasticsearch-master`):**
    To ensure the command `kubectl port-forward service/elasticsearch-master -n elastic 9200:9200` continues to work, a new Kubernetes Service named `elasticsearch-master` was created (e.g., `es-alias-service.yaml`):
    * `metadata.name`: `elasticsearch-master`
    * `metadata.namespace`: `elastic`
    * `spec.selector`: Configured to match the labels of the pods in the `es-cluster-eck-v901` ECK Elasticsearch cluster (e.g., `elasticsearch.k8s.elastic.co/cluster-name: "es-cluster-eck-v901"`).
    * `spec.ports`: Exposed TCP port `9200` (HTTP) and `9300` (Transport).
    ```bash
    kubectl apply -f es-alias-service.yaml
    ```

### 3.2. Kibana 9.0.1 Deployment

1.  **Define Kibana Custom Resource (CR):**
    A `Kibana` CRD (e.g., `kibana-eck.yaml`) was created:
    * `metadata.name`: `kibana-eck-v901` (example name for the ECK-managed Kibana instance)
    * `metadata.namespace`: `elastic`
    * `spec.version`: `"9.0.1"`
    * `spec.count`: `1`
    * `spec.elasticsearchRef.name`: `"es-cluster-eck-v901"` (linking to the new ECK Elasticsearch cluster)

2.  **Apply Kibana CR:**
    ```bash
    kubectl apply -f kibana-eck.yaml
    ```
    The deployment and readiness of the Kibana pod were monitored.

3.  **Create Alias Service for Kibana (`kibana-kibana`):**
    To ensure the command `kubectl port-forward service/kibana-kibana -n elastic 5601:5601` continues to work, a new Kubernetes Service named `kibana-kibana` was created (e.g., `kibana-alias-service.yaml`):
    * `metadata.name`: `kibana-kibana`
    * `metadata.namespace`: `elastic`
    * `spec.selector`: Configured to match the labels of the pods in the `kibana-eck-v901` ECK Kibana instance (e.g., `kibana.k8s.elastic.co/name: "kibana-eck-v901"`).
    * `spec.ports`: Exposed TCP port `5601`.
    ```bash
    kubectl apply -f kibana-alias-service.yaml
    ```

---

## 4. Verification

The new deployment was verified by:

1.  **Using the original `kubectl port-forward` commands:**
    ```bash
    kubectl port-forward service/elasticsearch-master -n elastic 9200:9200
    # In another terminal:
    # curl -k -u "elastic:<retrieved_password>" "https://localhost:9200/_cluster/health?pretty"

    kubectl port-forward service/kibana-kibana -n elastic 5601:5601
    # Accessed Kibana via https://localhost:5601 in a browser, logged in with the elastic user.
    ```
2.  Confirming connectivity between Kibana and Elasticsearch.
3.  Noting that ECK defaults to HTTPS for Elasticsearch and Kibana, so access methods might require acknowledging self-signed certificates (e.g., `curl -k` or browser exceptions) for initial local testing via port-forwarding.

---

## 5. Outcome and Important Notes

* A fresh, ECK-managed Elasticsearch 9.0.1 and Kibana 9.0.1 stack is now running in the `elastic` namespace.
* The old data was not preserved, as per the requirement.
* Legacy `kubectl port-forward` commands remain functional due to the creation of alias services (`elasticsearch-master`, `kibana-kibana`).
* For new configurations, Ingress rules, or internal cluster communication, it is recommended to use the service names generated by ECK (e.g., `es-cluster-eck-v901-es-http`, `kibana-eck-v901-kb-http`) as they are directly managed by the ECK lifecycle.
* All future configurations and upgrades for Elasticsearch and Kibana should be managed by modifying their respective ECK Custom Resource definitions.
* Security (TLS certificates, user management) is now primarily managed by ECK. For production, consider configuring custom certificates or integrating with a certificate manager.

---
This document summarizes the steps taken to migrate the Elasticsearch and Kibana stack. For detailed YAML configurations, please refer to the individual `elasticsearch-eck.yaml`, `es-alias-service.yaml`, `kibana-eck.yaml`, and `kibana-alias-service.yaml` files used during the deployment.