#!/usr/bin/env python
from collections import defaultdict
from subprocess import PIPE, Popen
import shlex
from boto import ec2
import json
import os
import sys
import shutil

def default(obj, _default):
    if not obj:
        return _default
    else:
        return obj

class Config(object):
    def __init__(self, config):
        for k, v in config.items():
            setattr(self, k, v)

class DockerSwarm(object):
    def __init__(self, env, vpc, region, subnet, zone):
        self.env = env
        self.vpc = vpc
        self.region = region
        self.subnet = subnet
        self.zone = zone
        self.set_slave_pool = False
        self.set_manager_pool = False
        self.e_conn = ec2.connect_to_region(region)

    def sg_cluster(self):
        f = {'tag:env': self.env, 'tag:role': 'DockerSwarm'}
        tcp_ports = [2377, 7946, 4789]
        udp_ports = [7946, 4789]
        for x in self.e_conn.get_only_instances(filters=f):
            for group in x.groups:
                if group.name == "swarm-{0}".format(self.env):
                    sec_group = self.e_conn.get_all_security_groups([group.name])[0]
                    try:
                        [sec_group.authorize('tcp', x, x, src_group=sec_group) for x in tcp_ports]
                    except:
                        pass
                    try:
                        [sec_group.authorize('udp', x, x, src_group=sec_group) for x in udp_ports]
                    except:
                        pass
                    try:
                        sec_group.authorize(src_group=sec_group)
                    except:
                        pass

    def get_managers(self):
        f = {'tag:env': self.env,
             'tag:role': 'DockerSwarm',
             'tag:swarm': 'manager'}
        for x in self.e_conn.get_only_instances(filters=f):
            if x.update() == "running" and x.tags.get("manager") != "leader":
                yield x

    def get_slaves(self):
        f = {'tag:env': self.env,
             'tag:role': 'DockerSwarm',
             'tag:swarm': 'slave',
             'vpc_id': self.vpc}
        for x in self.e_conn.get_only_instances(filters=f):
            if x.update() == "running":
                yield x

    def _get_count(self):
        instances = dict()
        instances['managers'] = 0
        instances['slaves'] = 0
        f = {'tag:env': self.env, 'tag:role': 'DockerSwarm'}
        for x in self.e_conn.get_only_instances(filters=f):
            if x.update() != 'running':
                continue
            if x.tags.get('swarm') == "manager":
                instances['managers'] += 1
            elif x.tags.get('swarm') == "slave":
                instances['slaves'] += 1
        return instances

    def counts(self, _type):
        return self._get_count().get(_type  )

    def remove_node(self, node):
        # first drain the node
        cmd = "docker node update --availability drain"
        self.run(node, cmd)
        # then remove it
        cmd = "docker-machine rm {0} --force".format(node)
        self.run(node, cmd)

    def leave_node(self, node, force=False):
        cmd = "docker swarm leave"
        if force:
            cmd += " --force "
        managers = [x.tags.get("Name") for x in self.get_managers()]
        #if node in managers:
        #    cmd += " --force-new-cluster "
        self.run(node, cmd)

    def _ids(self, node_type):
        f = {'tag:env': self.env,
             'tag:role': 'DockerSwarm',
             'tag:swarm': node_type}
        ids = list()
        for x in self.e_conn.get_only_instances(filters=f):
            if x.update() == "running":
                ids.append(int(x.tags.get('node')))
        return ids

    @property
    def manager_ids(self):
        return self._ids('manager')

    @property
    def slave_ids(self):
        return self._ids('slave')

    def nodes(self, node):
        f = {"tag:Name": node}
        return [x.tags.get("Name") for x in self.e_conn.get_only_instances(filters=f)]

    def clean_nodes(self):
        cmd = 'docker-machine ls --format "{{ .Name }}"'
        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        machine_nodes = [x.strip() for x in out.splitlines()]
        for x in machine_nodes:
            if x not in self.nodes(x):
                self.remove_node(x)
        f = {'tag:env': self.env, 'tag:role': 'DockerSwarm'}
        for x in self.e_conn.get_only_instances(filters=f):
            if x.tags.get("Name") not in machine_nodes:
                x.terminate()


    def add_managers(self, instance_type):
        manager_ids = self.manager_ids
        max_id = max(default(manager_ids, [0]))
        manager_id = -1
        for x in range(1, max_id):
            if x not in self.manager_ids:
                manager_id = x
        if manager_id == -1:
            manager_id=int(max_id + 1)

        node_name = "swarm-{env}-manager-{manager_id}".format(env=self.env, manager_id=manager_id)
        self.e_conn.delete_key_pair(node_name)
        try:
            cache_dir = os.path.join(os.environ.get("HOME"), ".docker/machine/machines/{0}".format(node_name))
            if os.path.isdir(cache_dir):
                shutil.rmtree(cache_dir)
        except:
            pass
        cmd = "docker-machine create -d amazonec2 "
        cmd += "--amazonec2-vpc-id {vpc} "
        cmd += "--amazonec2-region {region} "
        cmd += "--amazonec2-zone {zone} "
        cmd += "--amazonec2-instance-type {0} ".format(instance_type)
        cmd += "--amazonec2-subnet-id {subnet} "
        cmd += "--amazonec2-security-group swarm-{env} "
        cmd += "--swarm "
        cmd += "--swarm-master "
        cmd += node_name
        print node_name

        cmd = cmd.format(**self.__dict__)
        p = Popen(shlex.split(cmd))
        out, err = p.communicate()
        if err:
            raise Exception("Could not create manager: {0}".format(err))

        f = {'tag:Name': node_name}
        for x in self.e_conn.get_only_instances(filters=f):
            if x.update() == "running":
                x.add_tag('swarm', 'manager')
                x.add_tag('env', self.env)
                x.add_tag('role', 'DockerSwarm')
                x.add_tag('node', manager_id)
                try:
                    self.leave_node(node_name, force=True)
                except:
                    pass
            return x
    

    def _set_env(self, node_name):
        p = Popen(shlex.split("docker-machine env {0}".format(node_name)), stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        for x in out.splitlines():
            fields = [x.strip("=") for x in x.split()[1].split('=')]
            if len(fields) == 2:
                key = fields[0]
                value = "".join(fields[1].split('"'))
                try:
                    del os.environ[key]
                except:
                    pass
                os.environ[key] = value


    def add_slaves(self, instance_type):
        slave_ids = self.slave_ids
        max_id = max(default(slave_ids, [0]))
        slave_id = -1
        for x in range(1, max_id):
            if x not in slave_ids:
                slave_id = x
        if slave_id == -1:
            slave_id=int(max_id + 1)

        node_name = "swarm-{env}-node-{slave_id}".format(env=self.env, slave_id=slave_id) 
        cmd = "docker-machine create -d amazonec2 "
        cmd += "--amazonec2-vpc-id {vpc} "
        cmd += "--amazonec2-region {region} "
        cmd += "--amazonec2-zone {zone} "
        cmd += "--amazonec2-instance-type {instance_type} ".format(
            instance_type=instance_type)
        cmd += "--amazonec2-subnet-id {subnet} "
        cmd += "--amazonec2-security-group swarm-{env} "
        cmd += "--swarm "
        cmd += node_name
        
        cmd = cmd.format(**self.__dict__)
        p = Popen(shlex.split(cmd))
        out, err = p.communicate()
        if err:
            raise Exception("Could not create slave: {0}".format(err))

        f = {'tag:Name': node_name}
        for x in self.e_conn.get_only_instances(filters=f):
            x.add_tag('swarm', 'slave')
            x.add_tag('env', self.env)
            x.add_tag('role', 'DockerSwarm')
            x.add_tag('node', slave_id)
            #self.leave_node(node_name, force=True)
        

    def _get_lead_manager(self):
        f = {'tag:env': self.env, 'tag:swarm': 'manager', 'tag:manager': 'leader'}
        for x in self.e_conn.get_only_instances(filters=f):
            if x.update() == "running":
                return x
        return False


    def init_manager(self):
        # cmd = "docker-machine env swarm-{env}-manager-{last_manager}; "
        # cmd = cmd.format(env=self.env, last_manager=int(self._get_count().get('managers')))
        manager_name = "swarm-{env}-manager-{first_manager}"
        manager_name = manager_name.format(env=self.env, 
                                           first_manager=min(self.manager_ids))
        print manager_name
        for x in self.e_conn.get_only_instances(filters={'tag:Name': manager_name}):
            if x.update() == "running":
                x.add_tag("manager", "leader")

        cmd = "docker swarm init" #.format(x.private_ip_address)
        # cmd += "2>&1 | grep token | awk '{ print $5 }'"
        self.run(manager_name, cmd)
    
    def run(self, node, cmd):
        self._set_env(node)
        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if err:
            raise Exception("Could not perform operation: {0}\n\n\t{1}\n\n\t{2}".format(err, cmd, node))
        return out

    def join_managers(self, force=False):
        cmd = "docker swarm join --token {0} {1}:2377"
        manager = self._get_lead_manager()
        if not manager:
            self.init_manager()
            self.join_managers(force=force)
        for x in self.get_managers():
            node_name = x.tags.get('Name')
            if node_name == manager:
                continue
            if force:
                try:
                    self.leave_node(x.tags.get('Name'), force=True)
                except:
                    pass

            cmd = cmd.format(self.manager_token, manager.private_ip_address)
            self.run(node_name, cmd)

    @property
    def manager_token(self):
        manager = self._get_lead_manager()
        manager_name = manager.tags.get('Name')
        cmd = "docker swarm join-token manager --quiet"
        out = self.run(manager_name, cmd)
        return out.strip()

    @property
    def worker_token(self):
        manager = self._get_lead_manager()
        manager_name = manager.tags.get('Name')
        cmd = "docker swarm join-token worker --quiet"
        out = self.run(manager_name, cmd)
        return out.strip()


    def join_slaves(self):
        cmd = "docker swarm join --token {0} {1}:2377"
        manager = [m for m in self.get_managers()].pop()
        for x in self.get_slaves():
            node_name = x.tags.get('Name')
            cmd = cmd.format(self.worker_token, manager.private_ip_address)
            self.run(node_name, cmd)

if __name__ == '__main__':
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.add_option('--config')
    parser.add_option('--reset', action='store_true', default=False)
    parser.add_option('--init', action='store_true', default=False)
    opt, arg = parser.parse_args()

    if not os.path.isfile(opt.config):
        sys.stderr.write("{0} does not exist\n".format(opt.config))
        sys.exit(1)

    with open(opt.config) as config:
        env_config = json.loads(config.read())


    swarm = DockerSwarm(env_config.get('env'), 
                        env_config.get('vpc'), 
                        env_config.get('region'),
                        env_config.get('subnet'),
                        env_config.get('zone'))

    error_set = False

    if opt.reset:
        try:
            swarm.leave_node(swarm._get_lead_manager(), force=True)
            swarm.remove_node(swarm._get_lead_manager())
        except:
            pass
        for x in swarm.get_managers():
            try:
                swarm.leave_node(x.tags.get('Name'), force=True)
                swarm.remove_node(x.tags.get("Name"))
            except:
                pass
            x.terminate()

        for x in swarm.get_managers():
            try:
                swarm.leave_node(x.tags.get('Name'), force=True)
                swarm.remove_node(x.tags.get("Name"))
            except:
                pass
            x.terminate()


    manager_count = default(swarm.counts('managers'), 0)
    mgr = Config(env_config.get('managers'))
    if manager_count < mgr.count:
        add_managers = int(mgr.count - manager_count)
        for x in range(add_managers):
            swarm.add_managers(mgr.instance_type)

    elif manager_count > mgr.count:
        sub_managers = int(manager_count-mgr.count)
        managers = sorted([x for x in swarm.get_managers()], key=lambda x: x.tags.get("Name"), reverse=True)
        for x in range(sub_managers):
            manager = managers[x]
            swarm.remove_node(manager.tags.get("Name"), force=True)

    try:
        if opt.reset:
            swarm.init_manager()
        swarm.join_managers()
    except Exception, e:
        sys.stderr.write("Couldt not configure masters:\n\n\t{0}".format(str(e)))
        error_set = True

    slave_counts = default(swarm.counts('slaves'), 0)
    slave = Config(env_config.get('slaves'))
    if manager_count < slave.count:
        add_managers = int(slave.count - manager_count)
        for x in range(add_managers):
            swarm.add_managers(slave.instance_type)

    elif slave_count > slave.count:
        sub_managers = int(slave_count-slave.count)
        managers = sorted([x for x in swarm.get_managers()], key=lambda x: x.tags.get("Name"), reverse=True)
        for x in range(sub_managers):
            manager = managers[x]
            swarm.leave_node(manager.tags.get("Name"))
            swarm.remove_node(manager.tags.get("Name"), force=True)

    try:
        swarm.join_slaves()
    except Exception, err:
        sys.stderr.write("Could not configure slaves:\n\n\t{0}".format(str(err)))
        error_set = True

    if error_set:
        sys.exit(1)






