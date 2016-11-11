#!/usr/bin/env python

import click
import socket
import subprocess
import sys
import time

def get_ip():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("gmail.com",80))
  result = s.getsockname()[0]
  s.close()
  return result

def call_output(cmd):
  return subprocess.check_output(cmd)

def call_interactive(cmd):
  p = subprocess.Popen(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
  p.communicate()

def call(cmd):
  subprocess.call(cmd)

def cmd(host, cmd, options=[]):
  call(["ssh", 'pirate@%s' % host] + options + [cmd])

def cp(host, src, dst):
  call(["scp", src, "pirate@%s:%s" % (host, dst)])

@click.group(chain=True)
@click.option('--host', '-h', help='IP or host of Pi for chained commandos')
@click.pass_context
def main(ctx, host):
  """Programm which helps you to setup a Kubernetes Cluster with Raspberry Pis"""
  ctx.obj['host'] = host

@click.command()
@click.option('--image', '-i', default='https://github.com/hypriot/image-builder-rpi/releases/download/v1.1.0/hypriotos-rpi-v1.1.0.img.zip', help='WiFi password')
@click.option('--hostname', '-n', help='Pi hostname, e.g. k8s-worker-1')
@click.option('--ssid', '-s', help='WiFi SSID')
@click.option('--password', '-p', help='WiFi password')
@click.pass_context
def flash(ctx, image, hostname, ssid, password):
  """Flashes an image onto a SD card"""
  print "> flashing"
  uname = call_output(["uname", "-s"]).strip()
  call(["curl", "-O", "https://raw.githubusercontent.com/hypriot/flash/master/%s/flash" % uname])
  call("chmod +x flash".split(' '))
  call_interactive(("./flash -n %s -s %s -p %s %s" % (hostname, ssid, password, image)).split(" "))

@click.command()
@click.pass_context
@click.option('--subnetwork', '-s', default=None, help='Subnetwork of Pis')
@click.option('--watch/--no-watch', '-w', default=False, help='Watch repeatedly')
@click.option('--delay', '-d', default=2, help='Delay between watch requests')
def search(ctx, subnetwork, watch, delay):
  """Searches for Pis in the local network"""
  print "> searching pis"
  if subnetwork is None:
    subnetwork = get_ip()
    print ">> using ip %s" % subnetwork

  while True:
    result = call_output(("sudo nmap -sP %s/24" % subnetwork).split(" "))
    with open("file.tmp", "w") as f:
      f.write(result)

    pi_ips = call_output(["awk", '/^Nmap/{ip=$NF; name=$5}/B8:27:EB/{print name ": " ip}', "file.tmp"])
    print pi_ips

    if watch:
      time.sleep(delay)
    else:
      break

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def setup_ssh(ctx, host):
  if host is None:
    host = ctx.obj['host']

  """Copies your public ssh key to the Pi"""
  print "> installing ssh key on pi"
  print ">> note: password is: hypriot"
  print ">> note: if a warning with remote host id changed appears: delete ip from ~/.ssh/known_hosts"
  call(["ssh-copy-id", "pirate@%s" % host])

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def copy_config(ctx, host):
  if host is None:
    host = ctx.obj['host']

  """Copies the config files from prepare-home to the Pi (! hard-coded)"""
  print "> copying config files to pi"
  cp(host, "prepare-home/.tmux.conf", "~/.tmux.conf")
  cp(host, "prepare-home/.vimrc", "~/.vimrc")
  cp(host, "prepare-home/.bash_history", "~/.bash_history")

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def upgrade(ctx, host):
  if host is None:
    host = ctx.obj['host']

  """Upgrades all packages on Pi (recommended)"""
  print "> upgrading pi"
  cmd(host, "sudo apt-get -y update && sudo apt-get -y upgrade")

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.option('--tools', '-t', default=["tmux", "vim", "unzip"], multiple=True, help='Tools to install, multiple options allowed')
@click.pass_context
def install(ctx, host, tools):
  if host is None:
    host = ctx.obj['host']

  """Installs required tools"""
  tool_str = " ".join(tools)
  print "> installing tools: %s" % tool_str
  cmd(host, "sudo apt-get -y install %s" % tool_str)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.option('--sleep', '-s', default=5, help='Sleep after restart commando was executed')
@click.pass_context
def restart(ctx, host, sleep):
  if host is None:
    host = ctx.obj['host']

  """Restarts Pi and waits some seconds"""
  print "> restarting pi, wait %ss" % sleep
  cmd(host, "{ sleep 1; reboot -f; } >/dev/null &")
  time.sleep(sleep)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def login(ctx, host):
  if host is None:
    host = ctx.obj['host']

  """Login into Pi with tmux (either attach or create new session)"""
  print "> login to pi"
  cmd(host, "tmux new-session -s user || tmux attach-session -t user", ["-t"])

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def prepare_k8s(ctx, host):
  if host is None:
    host = ctx.obj['host']

  """Downloads and unzips files for Kubernetes Cluster (! hard-coded)"""
  print "> preparing k8s"
  cmd(host, "curl -L -o k8s-on-rpi.zip https://github.com/mputz86/k8s-on-rpi/archive/k8s-1.3.zip")
  folder = "k8s-on-rpi-k8s-1.3"
  bakFolder = "%s.bak" % folder
  cmd(host, "rm -fR %s" % bakFolder)
  cmd(host, "mv %s %s" % (folder, bakFolder))
  cmd(host, "unzip k8s-on-rpi.zip")

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def k8s_master_install(ctx, host):
  if host is None:
    host = ctx.obj['host']

  """Installs a Kubernetes Master Node on the Pi"""
  print "> install k8s master"
  folder = "k8s-on-rpi-k8s-1.3"
  cmd(host, "cd %s && sudo ./install-k8s-master.sh" % folder)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def k8s_worker_install(ctx, host):
  if host is None:
    host = ctx.obj['host']

  """Installs a Kubernetes Worker Node on the Pi"""
  print "> install k8s worker"
  folder = "k8s-on-rpi-k8s-1.3"
  cmd(host, "cd %s && sudo ./install-k8s-worker.sh" % folder)

if __name__ == '__main__':
  main.add_command(flash)
  main.add_command(search)
  main.add_command(setup_ssh)
  main.add_command(copy_config)
  main.add_command(upgrade)
  main.add_command(install)
  main.add_command(restart)
  main.add_command(prepare_k8s)
  main.add_command(k8s_master_install)
  main.add_command(k8s_worker_install)
  main.add_command(login)
  main(obj={})
