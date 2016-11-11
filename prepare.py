#!/usr/bin/env python

import click
import subprocess
import sys
import time

def call_output(cmd):
  return subprocess.check_output(cmd)

def call(cmd):
  subprocess.call(cmd)

def cmd(host, cmd, options=[]):
  call(["ssh", 'pirate@%s' % host] + options + [cmd])

def cp(host, src, dst):
  call(["scp", src, "pirate@%s:%s" % (host, dst)])

@click.group(chain=True)
@click.option('--host', '-h', help='pi host')
@click.pass_context
def main(ctx, host):
  ctx.obj['host'] = host

@click.command()
@click.option('--image', '-i', default='https://github.com/hypriot/image-builder-rpi/releases/download/v1.1.0/hypriotos-rpi-v1.1.0.img.zip', help='WiFi password')
@click.option('--hostname', help='pi hostname, eg k8s-worker-1')
@click.option('--ssid', '-s', help='WiFi SSID')
@click.option('--password', '-p', help='WiFi password')
@click.pass_context
def flash(ctx, image, hostname, ssid, password):
  print "> flashing"
  host = ctx.obj['host']
  uname = call_output(["uname", "-s"]).strip()
  cmd = "curl -O https://raw.githubusercontent.com/hypriot/flash/master/%s/flash" % uname
  print cmd
  call(["curl", "-O", "https://raw.githubusercontent.com/hypriot/flash/master/%s/flash" % uname])
  call("chmod +x flash".split(' '))
  call(("./flash %s -n %s -s %s -p %s" % (image, hostname, ssid, password)).split(" "))

@click.command()
@click.pass_context
def setup_ssh(ctx):
  print "> installing ssh key on pi"
  host = ctx.obj['host']
  cmd = "ssh-copy-id pirate@%s" % host
  call("ssh-copy-id pirate@%s" % host)

@click.command()
@click.pass_context
def copy_config(ctx):
  print "> copying config files to pi"
  host = ctx.obj['host']
  cp(host, "prepare-home/.tmux.conf", "~/.tmux.conf")
  cp(host, "prepare-home/.vimrc", "~/.vimrc")
  cp(host, "prepare-home/.bash_history", "~/.bash_history")

@click.command()
@click.pass_context
def upgrade(ctx):
  host = ctx.obj['host']
  print "> upgrading pi"
  cmd(host, "sudo apt-get -y update && sudo apt-get -y upgrade")

@click.command()
@click.pass_context
def install(ctx):
  print "> installing tools"
  host = ctx.obj['host']
  cmd(host, "sudo apt-get -y install tmux vim unzip")

@click.command()
@click.pass_context
def restart(ctx):
  print "> restarting pi"
  host = ctx.obj['host']
  cmd(host, "'{ sleep 1; reboot -f; } >/dev/null &'")
  time.sleep(5)

@click.command()
@click.pass_context
def prepare_k8s(ctx):
  host = ctx.obj['host']
  print "> preparing k8s"
  cmd(host, "curl -L -o k8s-on-rpi.zip https://github.com/mputz86/k8s-on-rpi/archive/k8s-1.3.zip")
  folder = "k8s-on-rpi-k8s-1.3"
  bakFolder = "%s.bak" % folder
  cmd(host, "rm -fR %s" % bakFolder)
  cmd(host, "mv %s %s" % (folder, bakFolder))
  cmd(host, "unzip k8s-on-rpi.zip")

@click.command()
@click.pass_context
def k8s_master_install(ctx):
  host = ctx.obj['host']
  print "> install k8s master"
  folder = "k8s-on-rpi-k8s-1.3"
  cmd(host, "cd %s && sudo ./install-k8s-master.sh" % folder)

@click.command()
@click.pass_context
def k8s_worker_install(ctx):
  host = ctx.obj['host']
  print "> install k8s worker"
  folder = "k8s-on-rpi-k8s-1.3"
  cmd(host, "cd %s && sudo ./install-k8s-worker.sh" % folder)

@click.command()
@click.pass_context
def login(ctx):
  print "> login to pi"
  host = ctx.obj['host']
  cmd(host, "tmux new-session -s user || tmux attach-session -t user", ["-t"])

if __name__ == '__main__':
  main.add_command(flash)
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
