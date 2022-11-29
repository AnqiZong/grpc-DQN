import random
import tensorflow as tf
import numpy as np
from kubernetes import client, config
from gym import spaces
import numpy as np
from kubernetes.client import ApiException


def getK8sClient():
    config_file = "D:/workspace/python/grpc-DQN//Config/config"
    # config.load_kube_config(config_file=config_file)
    config.kube_config.load_kube_config(config_file=config_file)
    # 获取API的CoreV1Api和BatchV1Api版本对象
    # Api_Instance = client.CoreV1Api()
    # nodeList = Api_Instance.list_node()
    # nodeList = client.V1NodeList().list_node()
    # arr = np.array([[0, 0, 0] * 2] * 3)
    # print(arr)

    # for node in nodeList.items:
    #    print(node.status.allocatable['memory'][:-2])
    return client


def createTestNamespace():
    k8sclient = getK8sClient()
    ns = k8sclient.V1Namespace()
    ns.metadata = k8sclient.V1ObjectMeta(name="dqntestenv")
    try:
        api_response = k8sclient.CoreV1Api().create_namespace(body=ns, pretty="true")
    except client.exceptions.ApiException:
        return
    return api_response


def deleteTestPods():
    print("Starting to delete pods in test namespace ...")
    api_response = getK8sClient().CoreV1Api().delete_collection_namespaced_pod("dqntestenv")
    print("delete pods in test namespace finished ...")
    return api_response


def createTestPod(index, schedulerName='dqn-scheduler'):
    api_instance = getK8sClient().CoreV1Api()
    name = 'test' + str(index)
    serviceIndex = random.randint(0, 10)
    roleIndex = random.randint(0, 10)
    cpuReqest = random.randint(1, 100)
    memoryRequest = random.randint(20, 200)
    storageRequest = random.randint(10, 100)
    # random.randint(101, 121)
    resp = None
    try:
        resp = api_instance.read_namespaced_pod(name=name, namespace='dqntestenv')
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            exit(1)
    if not resp:
        print("Pod %s does not exist. Creating it..." % name)
        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': name,
                'labels': {
                    'servicename': 'service' + str(serviceIndex),
                    'servicerolename': 'role' + str(roleIndex),
                }
            },
            'spec': {
                'schedulerName': schedulerName,
                'containers': [{
                    'image': 'nginx:1.12.1',
                    'name': 'nginx',
                    'resources': {
                        'requests': {
                            'cpu': str(cpuReqest) + 'm',
                            'memory': str(memoryRequest) + 'Mi',
                            'ephemeral-storage': str(storageRequest) + 'Mi'
                        }
                    }
                }]
            }
        }
        api_instance.create_namespaced_pod(namespace='dqntestenv', body=pod_manifest)


# if __name__ == '__main__':
    # data = {}
    # data.
    # for i in range(20):
    #     createTestPod(i, 'default-scheduler')
    # dataset = [[1, 2, 3], [1, 1, 1, ]]
    # dataset = np.array([0, 0, 0, 0, 0, 0] * 3)
    # dataset = [1, 2, 3]
    # print(dataset.shape)
    # for i in range(3):
    #     dataset.append(i)
    # print(dataset)
    # deleteTestPods()
    # createTestPod(11, 'default-scheduler')
    # nodeList = len(getK8sClient().V1NodeList().getItems())
    # nodeList = getK8sClient().CoreV1Api().list_node()
    # nodeNum = 0
    # for node in nodeList.items:
    #     print(node.metadata.name)
    #     nodeNum = nodeNum + 1
    # print(nodeNum)
