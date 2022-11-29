import time

from proto import GetDqnDataApi_pb2, GetDqnDataApi_pb2_grpc
import grpc
from concurrent import futures
from DQN import k8s_env as k8senv
from utils.globalVariable import glob_dict


# glob_dict.set_value("qVersion", 0)


# qVersion = 0


class UseDQN(GetDqnDataApi_pb2_grpc.UseDQNServicer):

    def GetQValues(self, request, context):
        # global qVersion
        print("Starts running DQN...")
        # global qVersion
        k8senv.K8sEnv.updateDQNArgs(request)
        print(" k8senv.K8sEnv.updateDQNArgs success!")
        # qVersion = qVersion + 1
        # print("server id is " + str(id(glob_dict)))
        # qVersion = qVersion + 1
        glob_dict.set_value("qVersion", int(glob_dict.get_value("qVersion")) + 1)
        # print("change qVersion is "+str(glob_dict.get_value("qVersion")))
        while int(glob_dict.get_value("qVersion")) != int(glob_dict.get_value("qChange")):
            time.sleep(3)
            print("qVersion is "+str(glob_dict.get_value("qVersion"))+" qChange is "+str(glob_dict.get_value("qChange")))
            continue
        nodesScore = k8senv.K8sEnv.getQvalues()
        print("nodesScore" + str(nodesScore))
        arr = []
        for score in nodesScore:
            arr.append(int(score))
        # print("request" + str(request))
        print(GetDqnDataApi_pb2.Response(qValues=arr))
        # print("success!!")
        return GetDqnDataApi_pb2.Response(qValues=arr)


def serverStart():
    # 1. 实例化server
    servers = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 2. 注册逻辑到server
    GetDqnDataApi_pb2_grpc.add_UseDQNServicer_to_server(UseDQN(), servers)
    # 3.启动 remoteServer
    servers.add_insecure_port('[::]:50051')
    servers.start()
    servers.wait_for_termination()

