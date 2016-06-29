#import os
#import platform
#import yaml
#from subprocess import check_call

from charms.ractive.helpers import is_state
from charms.ractive.bus import set_state
from charms.ractive.bus import get_state
from charms.ractive.bus import remove_state
from charms.reactive.decorators import hook
from charms.reactive.decorators import when
from charms.reactive.decorators import when_not

from charms.layer.hpccsystems_platform import HPCCSystemsPlatformConfigs
from charms.layer.utils import SSHKey

@hook('install')
def install_platform():
    if reactive.is_state('platform.available'):
        return
    platform = HPCCSystemsPlatformConfigs()
    platform.install_prerequsites()
    platform.install_platform()
    # ssh keys?
    config = hookenv.config()
    if config['ssh-key-private'] 
        install_keys_from_config(config)
    reactive.set_state('platform.installed')
    #platform.open_ports()

@hook('config-changed')
def config_changed():
    config = hooken.config()
    if config.changed('ssh-key-private'): 
        install_keys_from_config(config)

    platform = HPCCSystemsPlatformConfigs()
    if config.changed('hpcc-version') || config.changed(hpcc-type): 
       hpcc_installed = platform.installed_platform()
       if (config.changed(hpcc-version) != hpcc_installed[0]) ||
          (config.changed(hpcc-type) != hpcc_installed[1]) : 
          reactive.remove_state('platform.installed')
          platform.uninstall_platform()
          platform.install_platform()
          reactive.set_state('platform.installed')
 


def install_keys_from_config(config):
    sshKey = SSHKey('hpcc', 'hpcc', '/home/hpcc') 
    priKey =  config['ssh-key-private'] 
    pubKey =  config['ssh-key-public'] 
    sshKey.install_key(priKey, pubKey)
    reactive.set_state('platform.sshkeys.changed')
    
