#!/usr/bin/env python3

import os
import platform
import yaml
import re
# python 2.7
#import ConfigParser
# python 3
#import Configparser
from subprocess import check_call,check_output,CalledProcessError
 
from charmhelpers import fetch
from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import log
# log level: CRITICAL,ERROR,WARNING,INFO,DEBUG
from charmhelpers.core.hookenv import CRITICAL
from charmhelpers.core.hookenv import ERROR
from charmhelpers.core.hookenv import WARNING
from charmhelpers.core.hookenv import INFO
from charmhelpers.core.hookenv import DEBUG
#from charmhelpers.core import templating

import charms.layer.utils


from charmhelpers.fetch.archiveurl import (
    ArchiveUrlFetchHandler
)

#import charm.apt
   
class HPCCEnv:
   JUJU_HPCC_DIR    = '/var/lib/HPCCSystems/charm'
   CONFIG_DIR       = '/etc/HPCCSystems'
   ENV_XML_FILE     = 'environment.xml'
   ENV_CONF_FILE    = 'environment.conf'
   ENV_RULES_FILE   = 'genenvrules.conf'
   HPCC_HOME        = '/opt/HPCCSystems'
   HPCC_CLUSTER_DIR = JUJU_HPCC_DIR + '/cluster'
   CLUSTER_IPS_DIR  = HPCC_CLUSTER_DIR +  '/ips'
   CLUSTER_NODE_TYPES = ['dali',
                         'sasha', 
                         'dfuserver',
                         'eclagent',
                         'eclccserver',
                         'eclscheduler',
                         'esp',
                         'roxie',
                         'thormaster',
                         'thorslave',
                         'support']
   PLATFORM_COMPONENTS = ['dali',
                         'sasha', 
                         'dfuserver',
                         'eclagent',
                         'eclccserver',
                         'eclscheduler',
                         'esp',
                         'roxie',
                         'thor',
                         'dafilesrv']
 
     

class HPCCSystemsPlatformConfigs:
    def __init__(self):
        self.config = hookenv.config()
        #log("config.yaml:", INFO)
        #for key in self.config:
        #   log("%s : %s" % (key, self.config[key]),  INFO)
        self.version = self.config['hpcc-version']
        self.nodes = {}
        
    def install(self):
        self.install_prerequisites(self.config['hpcc-type']) 
        self.install_platform()

    def get_platform_package_name(self):
        hpcc_type = self.config['hpcc-type']
        full_hpcc_type = {"CE":"community", "EE":"enterprise", "LN":"internal"}
        return "hpccsystems-platform-" + full_hpcc_type[hpcc_type] + "_" +  \
               self.config['hpcc-version'] + platform.linux_distribution()[2] + "_amd64.deb"

    def get_platform_package_url(self):
        hpcc_version_mmp = (self.config['hpcc-version']).split('-',1)[0]
        return self.config['base-url'] + "/" + self.config['hpcc-type'] + "-Candidate-" + \
               hpcc_version_mmp + "/bin/platform/" + self.get_platform_package_name()

    def download_platform(self):
        hookenv.status_set('maintenance', 'Downloading platform')
        url = self.get_platform_package_url()
        package = self.get_platform_package_name()
        log("Platform package url: " + url, INFO)
        aufh =  ArchiveUrlFetchHandler()
        dest_file = "/tmp/" + package
        aufh.download(url, dest_file)
        fetch.apt_update()
        checksum = self.config['package-checksum']
        if checksum:
            hash_type = self.config['hash-type']
            if not hash_type:
                hash_type = 'md5'
            host.check_hash(dest_file, checksum, hash_type)
        return dest_file

    def install_platform(self):
        hookenv.status_set('maintenance', 'Installing platform')
        package_file = self.download_platform()
        dpkg_install_platform_deb = 'dpkg -i %s' % package_file
        check_call(dpkg_install_platform_deb.split(), shell=False)

    def uninstall_platform(self):
        hookenv.status_set('maintenance', 'Uninstalling platform')
        dpkg_uninstall_platform_deb = 'dpkg --purage hpccsystems-platform'
        check_call(dpkg_uninstall_platform_deb.split(), shell=False)

    def installed_platform(self):
        p = re.compile(r".*hpccsystems-platform[\s]+([^\s]+)\s+([^\s]+)[\s]+hpccsystems-platform-([^\s]+)\\.*", re.M)
        try:
            hpcc_type = {"community":"CE", "enterprise":"EE", "internal":"LN"}
            output = check_output(['dpkg-query', '-l', 'hpccsystems-platform'])
            m = p.match(str(output))
            if m:
                return [m.group(1),hpcc_type[m.group(3)],m.group(3),m.group(2)]
            else:
                return ['','','','']
        except CalledProcessError:
             return ['','','','']

    def install_prerequsites(self):
        hookenv.status_set('maintenance', 'Installing prerequisites')
        charm_dir = hookenv.charm_dir()

        prereq_dir =  charm_dir + '/dependencies/' + platform.linux_distribution()[2] 
        with open(os.path.join(prereq_dir,'community.yaml')) as fp:
            workload = yaml.safe_load(fp)
        packages = workload['packages']
        addition_file = ""
        hpcc_type = self.config['hpcc-type']
        if hpcc_type == "EE":
            addition_file = os.path.join(prereq_dir, "enterprise.yaml")
        elif hpcc_type == "LN":
            addition_file = os.path.join(prereq_dir, "internal.yaml")
        if addition_file:
            with open(addition_file) as fp:
                workload = yaml.safe_load(fp)
            packages.extend(workload['packages'])
        fetch.apt_install(fetch.filter_installed_packages(packages))

    def open_ports(self):
        hookenv.status_set('maintenance', 'Open ports')
        #hookenv.open_port(self.config['esp-port'], 'TCP')
        hookenv.open_port(8010, 'TCP')
        hookenv.open_port(8002, 'TCP')
        hookenv.open_port(8015, 'TCP')
        hookenv.open_port(9876, 'TCP')
        #hookenv.open_port(self.config['esp-secure-port'], 'TCP')
        hookenv.open_port(18010, 'TCP')
        hookenv.open_port(18002, 'TCP')
        hookenv.open_port(18008, 'TCP')

    def start(self):
        hookenv.status_set('maintenance', 'Starting HPCC')
        log(HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init start', INFO)
        try: 
            output = check_output([HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init', 'start'])
            log(output, INFO)
        except CalledProcessError:
            log(output, ERROR)
            return 1

    def stop(self):
        hookenv.status_set('maintenance', 'Stopping HPCC')
        log(HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init stop', INFO)
        try: 
            output = check_output([HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init', 'stop'])
            log(output, INFO)
        except CalledProcessError:
            log(output, ERROR)
            return 1

    def restart(self):
        hookenv.status_set('maintenance', 'Restarting HPCC')
        log(HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init stop', INFO)
        try: 
            output = check_output([HPCCEnv.HPCC_HOME+'/etc/init.d/hpcc-init', 'restart'])
            log(output, INFO)
        except CalledProcessError:
            log(output, ERROR)
            return 1

    def generate_env_xml(self, nodeTypes):
        self.process_nodes(nodeTypes)
        # future, create yaml file for envgen
        # self.create_envgen_yaml()
        #check_call(dpkg_install_platform_deb.split(), shell=False)
        cmd = self.create_envgen_cmd()
        log(cmd, INFO)
        try:
            output =  check_call(cmd.split(), shell=False)
            log(output, INFO)
        except CalledProcessError:
            log(output, ERROR)
            return 1
  
    def create_envgen_yaml(self):
        pass

    # when create_envgen_yaml available no need for this 
    def create_envgen_cmd(self):
        cmd = HPCCEnv.HPCC_HOME + '/sbin/envgen -env ' + \
              HPCCEnv.CONFIG_DIR + '/' +  HPCCEnv.ENV_XML_FILE + \
              ' -override roxie,@roxieMulticastEnabled,false' + \
              ' -override thor,@replicateOutputs,true' + \
              ' -override esp,@method,htpasswd' + \
              ' -override thor,@replicateAsync,true'  
        for key in nodes.key():
            nodeType=key.split('_')[0] 
            if nodeType == 'support':
                with open( HPCCEnv.CLUSTER_IPS_DIR + '/' + key, 'r') as file:
                    ip = re.sub('[\s+]', '', file.read())
                cmd = cmd + ' -ip ' + ip + ' -supportnodes 1'
                continue
            if nodeType == 'thor':
               cmd = cmd + ' -thornodes ' + str(nodes[k]) + \
                     ' -slavesPerNode ' + self.config['slaves-per-node']
            elif nodeType == 'roxie':
               cmd = cmd + ' -roxienodes ' + str(nodes[k])  
            cmd = cmd + ' -assign_ips ' + nodeType + ':file ' +  \
                  HPCCEnv.CLUSTER_IPS_DIR + '/' + key
        return cmd
              
    def process_nodes(self, nodeTypes):
        self.node = {}
        for nodeType in nodeTypes:
            n =  self.nodes_per_type(nodeType)
            if n > 0:
                self.nodes[node_type] = n
            elif n == 0:
                log("Ip file % has no ip" % node_type, WARNING)
            elif n == -1:
                log("Ip file % doesn't exists" % node_type, WARNING)
       
    def verify_node_type(self, nodeType):
        pass

    def nodes_per_type(self, nodeType):
        ipFile =  HPCCEnv.CLUSTER_IPS_DIR + '/' + nodeType
        if not ipFile.exists:
            return -1
        i = 0
        with open(ipFile, 'r') as fp:          
            for line in fp:
                if utils.IP_FILE_PATTERN.match(line):
                    i = i + 1
        return i
          

# Sample config file:
# [default]
# k1=v1
# k2=v2
# cfgParser = ConfigParser.RawConfigParser()
#  cfgParser.read(r'<config file name>')
# value1 = cfgParser.get('default', 'k1')

