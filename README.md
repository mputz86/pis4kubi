
## Script for setting up Raspberry Pi Kubernetes Cluster

This script helps you to setup a raspberry pi cluster. Everything is base on [https://github.com/mputz86/k8s-on-rpi](https://github.com/mputz86/k8s-on-rpi) (thanks to [awassink](https://github.com/awassink) for his work in the [repository I forked](https://github.com/awassink/k8s-on-rpi)).

The script can be run via.

### Workflow

Described is the workflow for setting up a master node. For any worker, replace 'master-1' with the appropriate worker name, like 'worker-1'.

- insert SD card in your linux / mac machine

- flash image on SD card; set WiFi and hostname if desired

    ./pis4kubi.py flash -s AndroidAP -p password -n k8s-master-1

- insert SD card in Pi and power on

- search for Pi (-w for watching)

    ./pis4kubi.py search -w

- configure ssh: requires the password of the Raspberry Pi admin, 'hypriot'

    ./pis4kubi.py -h k8s-master-1 setup_ssh

- preparations (multi-command execution; note: restart after upgrade is important!)

    ./pis4kubi.py -h k8s-master-1 copy_config upgrade install restart prepare_k8s

- install k8s-master (or worker)

    ./pis4kubi.py -h k8s-master-1 k8s_master_install


### Useful Tools

- search for Pi (-w for watching)

    ./pis4kubi.py search -w

- log into machine for analyzing / see logs / ..

    ./pis4kubi.py -h k8s-master-1 login


### Additional references

[http://blog.kubernetes.io/2015/12/creating-raspberry-pi-cluster-running.html](http://blog.kubernetes.io/2015/12/creating-raspberry-pi-cluster-running.html)
