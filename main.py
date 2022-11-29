from remoteServer import server
from threading import Thread
import time
from DQN import run_this
from utils.globalVariable import glob_dict

if __name__ == '__main__':
    # 对神经网络初始化
    # matrix = np.float32(np.array([0] * 3))
    # print(matrix)
    # print(tianshou.__version__)
    # env_k8s.K8sEnv()
    print("main id " + str(id(glob_dict)))
    thread1 = Thread(target=server.serverStart)
    # thread1.setDaemon(True)
    thread1.start()
    time.sleep(40)
    thread2 = Thread(target=run_this.start_DQN)
    thread2.start()
    thread1.join()
    print('thread1 END!!')
    thread2.join()
    print('main finished!!!')
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
