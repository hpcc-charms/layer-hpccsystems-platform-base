#!/usr/bin/env python3
#import os
#import platform
#import yaml
#from subprocess import check_call

from charms.reactive.helpers import is_state
from charms.reactive.bus import set_state
from charms.reactive.bus import get_state
from charms.reactive.bus import remove_state
from charms.reactive.decorators import hook
from charms.reactive.decorators import when
from charms.reactive.decorators import when_not

from charmhelpers.core import hookenv 
from charmhelpers.core.hookenv import log
# log level: CRITICAL,ERROR,WARNING,INFO,DEBUG
from charmhelpers.core.hookenv import CRITICAL
from charmhelpers.core.hookenv import ERROR
from charmhelpers.core.hookenv import WARNING
from charmhelpers.core.hookenv import INFO
from charmhelpers.core.hookenv import DEBUG


from charms.layer.hpccsystems_platform import HPCCSystemsPlatformConfig
from charms.layer.utils import SSHKey

@when('plugin-config.restart.platform')
def restart_platform():
    if is_state('platform.started'):
       remove_state('platform.started')
    if is_state('platform.start.failed'):
       remove_state('platform.start.failed')
    remove_state('plugin-config.restart.platform')

    platform = HPCCSystemsPlatformConfig()
    if platform.restart():
       set_state('platform.start.failed')
       hookenv.status_set('blocked', 'hpcc start failed')
    else:
       set_state('platform.started')
       hookenv.status_set('active', 'started')

    
