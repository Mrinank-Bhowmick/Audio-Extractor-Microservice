### To pass the Certificate Authority (CA) certificate to the auth service, create a configmap with the CA certificate file.

``` bash
kubectl create configmap auth-certificate --from-file=cacert.pem
```

<details><summary>Output</summary>

``` bash
configmap/auth-credential created
```
</details>

<details><summary>How to check the configmap ?</summary>

``` bash
kubectl get configmap auth-certificate -o json
```
<details><summary>The output would look like this</summary>

### Where `cacert.pem` is the key used in [server.py](../server.py#L27) to read the certificate file.

## Output :
```
{
    "apiVersion": "v1",
    "data": {
```

        "cacert.pem": "FULL CONTENT OF THE CERTIFICATE"
    },
    
```
    "kind": "ConfigMap",
    "metadata": {
        "creationTimestamp": "2020-07-07T15:20:44Z",
        "name": "auth-certificate",
        "namespace": "default",
        "resourceVersion": "123456",
        "selfLink": "/api/v1/namespaces/default/configmaps/auth-certificate",
        "uid": "123456789"
    }
}
```
</details>


</details>
<details><summary>How Secrets Are Stored ?</summary>
<I> All the secrets are stored as environment variables in the auth deployment pod</I>
</details>

<details><summary>On which platfrom the database is hosted ?</summary>

* Mysql database is hosted on Planetscale platform.