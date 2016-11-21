
## Script for setting up Raspberry Pi Kubernetes Cluster

This script helps you to setup a Raspberry Pi cluster based on [HypriotOS](https://github.com/hypriot/image-builder-rpi/releases). Setting up the cluster is is base on [https://github.com/mputz86/k8s-on-rpi](https://github.com/mputz86/k8s-on-rpi) (thanks to [awassink](https://github.com/awassink) for his work in the [repository I forked](https://github.com/awassink/k8s-on-rpi)).


### Workflow

Described is the workflow for setting up a master node. For any worker, replace 'master-1' with the appropriate worker name, like 'worker-1'.

- insert SD card in your linux / mac machine

- flash image on SD card
    - set WiFi and hostname if desired
    - important: set the `-n k8s-master-1` unique in your cluster (eg k8s-worker-1 for the first worker node)
    - note: flashes [HypriotOS](https://github.com/hypriot/image-builder-rpi/releases) on the SD card

```
    ./pis4kubi.py flash -s AndroidAP -p password -n k8s-master-1
```

- insert SD card in Pi and power on

- search for Pi (-w for watching)

```
    ./pis4kubi.py search -w
```

- configure ssh: requires the password of the Raspberry Pi admin, 'hypriot'
    - note: `-h k8s-mater-1` is the hostname specified in the flashing step

```
    ./pis4kubi.py -h k8s-master-1 setup_ssh
```

- preparations
    - multi-command execution
    - restart after upgrade is important!
    - note: the last step downloads the [kubernetes setup files](https://github.com/mputz86/k8s-on-rpi)

```
    ./pis4kubi.py -h k8s-master-1 copy_config upgrade install restart prepare_k8s
```

- install k8s-master
    - important: for a worker node use `k8s_worker_install`

```
    ./pis4kubi.py -h k8s-master-1 k8s_master_install
```

### Useful Tools

- search for Pi (-w for watching)

```
    ./pis4kubi.py search -w
```

- log into machine for analyzing / see logs / ..

```
    ./pis4kubi.py -h k8s-master-1 login
```

### Known issues

* worker does not reconnect to cluster; solution
    - login to worker and
    - start docker service anew

```
    ./pis4kubi.py -h k8s-worker-1 login
```

```
    sudo systemctl restart docker.service
```


### Additional references

[http://blog.kubernetes.io/2015/12/creating-raspberry-pi-cluster-running.html](http://blog.kubernetes.io/2015/12/creating-raspberry-pi-cluster-running.html)
