sudo tail -f /var/log/syslog
sudo systemctl
sudo systemctl start docker-bootstrap.service
sudo systemctl stop docker-bootstrap.service
sudo systemctl restart docker-bootstrap.service
sudo systemctl start k8s-master.service
sudo systemctl stop k8s-master.service
sudo systemctl restart k8s-master.service
sudo systemctl start k8s-etcd.service
sudo systemctl stop k8s-etcd.service
sudo systemctl restart k8s-etcd.service
sudo systemctl start k8s-flannel.service
sudo systemctl stop k8s-flannel.service
sudo systemctl restart k8s-flannel.service
/usr/bin/docker -H unix:///var/run/docker-bootstrap.sock logs k8s-flannel
/usr/bin/docker -H unix:///var/run/docker-bootstrap.sock exec -ti k8s-flannel /bin/bash
