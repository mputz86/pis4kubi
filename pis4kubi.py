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

def call_output(cmd, verbose=False):
  if verbose:
    print ">> $ %s" % (" ".join(cmd))
  return subprocess.check_output(cmd)

def call_interactive(cmd, verbose=False):
  if verbose:
    print ">> $ %s" % (" ".join(cmd))
  p = subprocess.Popen(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
  p.communicate()

def call(cmd, verbose=False):
  if verbose:
    print ">> $ %s" % (" ".join(cmd))
  subprocess.call(cmd)

def cmd(host, cmd, options=[], verbose=False):
  call(["ssh", 'pirate@%s' % host] + options + [cmd], verbose=verbose)

def cp(host, src, dst, directory=False, verbose=False):
  options = []
  if directory:
    options.append("-r")
  call(["scp"] + options + [src, "pirate@%s:%s" % (host, dst)], verbose=verbose)

@click.group(chain=True)
@click.option('--host', '-h', help='IP or host of Pi for chained commandos')
@click.option('--verbose/--no-verbose', '-v', default=False, help='Print out verbose information')
@click.pass_context
def main(ctx, host, verbose):
  """Programm which helps you to setup a Kubernetes Cluster with Raspberry Pis"""
  ctx.obj['host'] = host
  ctx.obj['verbose'] = verbose

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
  verbose = ctx.obj['verbose']

  while True:
    result = call_output(("sudo nmap -sP %s/24" % subnetwork).split(" "), verbose=verbose)
    with open("file.tmp", "w") as f:
      f.write(result)

    pi_ips = call_output(["awk", '/^Nmap/{ip=$NF; name=$5}/B8:27:EB/{print name ": " ip}', "file.tmp"], verbose=verbose)
    print pi_ips

    if watch:
      if verbose:
        print ">> sleeping for %s seconds" % delay
      time.sleep(delay)
    else:
      break

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def setup_ssh(ctx, host):
  """Copies your public ssh key to the Pi"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  print "> installing ssh key on pi and removing host from ~/.ssh/known_hosts"
  print ">> note: password is: hypriot"
  print ">> note: if a warning with remote host id changed appears: delete ip from ~/.ssh/known_hosts"
  call(["ssh-keygen", "-R", host], verbose=verbose)
  call(["ssh-copy-id", "pirate@%s" % host], verbose=verbose)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def copy_config(ctx, host):
  """Copies the config files from prepare-home to the Pi (! hard-coded)"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  print "> copying config files to pi"
  cp(host, "prepare-home/.tmux.conf", "~/.tmux.conf", verbose=verbose)
  cp(host, "prepare-home/.vimrc", "~/.vimrc", verbose=verbose)
  cp(host, "prepare-home/.bash_history", "~/.bash_history", verbose=verbose)
  cmd(host, 'curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim', verbose=verbose)
  cmd(host, 'vim +PlugInstall +qall', verbose=verbose)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def upgrade(ctx, host):
  """Upgrades all packages on Pi (recommended)"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  print "> upgrading pi"
  cmd(host, "sudo apt-get -y update && sudo apt-get -y upgrade", verbose=verbose)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.option('--tools', '-t', default=["tmux", "vim", "unzip"], multiple=True, help='Tools to install, multiple options allowed')
@click.pass_context
def install(ctx, host, tools):
  """Installs required tools"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  tool_str = " ".join(tools)
  print "> installing tools: %s" % tool_str
  cmd(host, "sudo apt-get -y install %s" % tool_str, verbose=verbose)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.option('--sleep', '-s', default=30, help='Sleep after restart commando was executed')
@click.pass_context
def restart(ctx, host, sleep):
  """Restarts Pi and waits some seconds"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  print "> restarting pi, wait %ss" % sleep
  cmd(host, "{ sleep 1; sudo shutdown -r now; } >/dev/null &", verbose=verbose)
  time.sleep(sleep)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def login(ctx, host):
  """Login into Pi with tmux (either attach or create new session)"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  print "> login to pi"
  cmd(host, "tmux new-session -s user || tmux attach-session -t user", ["-t"], verbose=verbose)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def prepare_k8s(ctx, host):
  """Downloads and unzips files for Kubernetes Cluster (! hard-coded)"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  print "> preparing k8s"
  cmd(host, "curl -L -o k8s-on-rpi.zip https://github.com/mputz86/k8s-on-rpi/archive/k8s-1.3.zip")
  folder = "k8s-on-rpi-k8s-1.3"
  bakFolder = "%s.bak" % folder
  cmd(host, "rm -fR %s" % bakFolder, verbose=verbose)
  cmd(host, "mv %s %s" % (folder, bakFolder), verbose=verbose)
  cmd(host, "unzip k8s-on-rpi.zip", verbose=verbose)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.option('--directory', '-d', help='Directory which should be copied to Pi')
@click.pass_context
def copy(ctx, host, directory):
  """Copies the directory to Pi"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  print "> copying directory %s" % directory
  cp(host, directory, "~/", directory=True, verbose=verbose)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def k8s_master_install(ctx, host):
  """Installs a Kubernetes Master Node on the Pi"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  print "> install k8s master"
  folder = "k8s-on-rpi-k8s-1.3"
  cmd(host, "cd %s && sudo ./install-k8s-master.sh" % folder, verbose=verbose)

@click.command()
@click.option('--host', '-h', help='IP or host of Pi')
@click.pass_context
def k8s_worker_install(ctx, host):
  """Installs a Kubernetes Worker Node on the Pi"""
  if host is None:
    host = ctx.obj['host']
  verbose = ctx.obj['verbose']

  print "> install k8s worker"
  folder = "k8s-on-rpi-k8s-1.3"
  cmd(host, "cd %s && sudo ./install-k8s-worker.sh" % folder, verbose=verbose)

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
  main.add_command(copy)
  main(obj={})
