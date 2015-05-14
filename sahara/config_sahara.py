#!/usr/bin/env python
import baker
from neutronclient.neutron import client as neutron
from saharaclient.api import client as sahara


ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'openstack'
ADMIN_PROJECT_NAME = 'admin'
AUTH_URL = 'http://10.0.1.108:5000/v2.0'
NETWORK_URL = 'http://10.0.1.108:9696'
SAHARA_PROJECT_NAME = 'demo'


def sahara_client():
    return sahara.Client(auth_url=AUTH_URL,
                         username=ADMIN_USERNAME,
                         api_key=ADMIN_PASSWORD,
                         project_name=SAHARA_PROJECT_NAME)


def get_public_private_nets():
    '''Returns (public id, private id).'''
    client = neutron.Client(api_version='2.0',
                            auth_url=AUTH_URL,
                            endpoint_url=NETWORK_URL,
                            username=ADMIN_USERNAME,
                            password=ADMIN_PASSWORD,
                            tenant_name=ADMIN_PROJECT_NAME)
    retval = {}
    for net in client.list_networks().get('networks', []):
        if net.get('name') in ['public', 'private']:
            retval[net.get('name')] = net.get('id')
    return (retval.get('public'), retval.get('private'))


def cluster_template_cdh5(name=None):
    name = 'cdh5' if not name else name
    float_pool, mgmt_net = get_public_private_nets()
    return {
        'name': name,
        'plugin_name': 'cdh',
        'hadoop_version': '5',
        'net_id': mgmt_net,
        'cluster_configs': {},
        'node_groups': [
            {
                'count': 1,
                'name': 'cdh-namenode',
                'flavor_id': '4',
                'node_processes': ['HDFS_NAMENODE',
                                   'HIVE_SERVER2',
                                   'HIVE_METASTORE',
                                   'YARN_RESOURCEMANAGER',
                                   'CLOUDERA_MANAGER'],
                'floating_ip_pool': float_pool
            },
            {
                'count': 1,
                'name': 'cdh-secondarynamenode',
                'flavor_id': '2',
                'node_processes': ['HDFS_SECONDARYNAMENODE',
                                   'OOZIE_SERVER',
                                   'YARN_JOBHISTORY'],
                'floating_ip_pool': float_pool
            },
            {
                'count': 3,
                'name': 'cdh-datanode',
                'flavor_id': '2',
                'node_processes': ['HDFS_DATANODE',
                                   'YARN_NODEMANAGER'],
                'floating_ip_pool': float_pool
            }
        ]
    }


def cluster_template_vanilla26(name=None):
    name = 'vanilla26' if not name else name
    float_pool, mgmt_net = get_public_private_nets()
    return {
        'name': name,
        'plugin_name': 'vanilla',
        'hadoop_version': '2.6.0',
        'net_id': mgmt_net,
        'cluster_configs': {},
        'node_groups': [
            {
                'count': 1,
                'name': 'v26-master',
                'flavor_id': '2',
                'node_processes': ['namenode',
                                   'oozie',
                                   'resourcemanager',
                                   'historyserver'],
                'floating_ip_pool': float_pool
            },
            {
                'count': 3,
                'name': 'v26-worker',
                'flavor_id': '2',
                'node_processes': ['datanode',
                                   'nodemanager'],
                'floating_ip_pool': float_pool
            }
        ]
    }


def cluster_template_hdp2(name=None):
    name = 'hdp2' if not name else name
    float_pool, mgmt_net = get_public_private_nets()
    return {
        'name': name,
        'plugin_name': 'hdp',
        'hadoop_version': '2.0.6',
        'net_id': mgmt_net,
        'cluster_configs': {},
        'node_groups': [
            {
                'count': 1,
                'name': 'hdp2-master',
                'flavor_id': '2',
                'node_processes': ['NAMENODE',
                                   'SECONDARY_NAMENODE',
                                   'ZOOKEEPER_SERVER',
                                   'AMBARI_SERVER',
                                   'PIG',
                                   'HISTORYSERVER',
                                   'RESOURCEMANAGER',
                                   'OOZIE_SERVER',
                                   'GANGLIA_SERVER',
                                   'NAGIOS_SERVER'],
                'floating_ip_pool': float_pool
            },
            {
                'count': 3,
                'name': 'hdp2-worker',
                'flavor_id': '2',
                'node_processes': ['DATANODE',
                                   'HDFS_CLIENT',
                                   'MAPREDUCE2_CLIENT',
                                   'OOZIE_CLIENT',
                                   'NODEMANAGER'],
                'floating_ip_pool': float_pool
            }
        ]
    }


def create_cluster(ctfunc, name=None):
    client = sahara_client()
    template = ctfunc(name)
    return client.cluster_templates.create(**template)


@baker.command
def vanilla26(name=None):
    result = create_cluster(cluster_template_vanilla26, name)
    print(str(result))


@baker.command
def hdp2(name=None):
    result = create_cluster(cluster_template_hdp2, name)
    print(str(result))

@baker.command
def cdh5(name=None):
    result = create_cluster(cluster_template_cdh5, name)
    print(str(result))


baker.run()
