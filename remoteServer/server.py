from proto import GetDqnDataApi_pb2, GetDqnDataApi_pb2_grpc
import grpc
from concurrent import futures


class UseDQN(GetDqnDataApi_pb2_grpc.UseDQNServicer):
    def GetQValues(self, request, context):
        nodesScore = [78,89,33]
        return GetDqnDataApi_pb2.Response(qValues=nodesScore)


def serverStart():
    # 1. 实例化server
    servers = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 2. 注册逻辑到server
    GetDqnDataApi_pb2_grpc.add_UseDQNServicer_to_server(UseDQN(), servers)
    # 3.启动 remoteServer
    servers.add_insecure_port('[::]:50051')
    servers.start()
    servers.wait_for_termination()
