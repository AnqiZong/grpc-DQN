import k8sOperater
import numpy as np
import random
import datetime
from utils.globalVariable import glob_dict

testNum = 1


def getRandomNum(num):
    arr = np.zeros((num, 5))
    for i in range(0, num):
        arr[i][0] = random.randint(0, 10)
        arr[i][1] = random.randint(0, 10)
        arr[i][2] = random.randint(1, 600)
        arr[i][3] = random.randint(20, 500)
        arr[i][4] = random.randint(50, 500)
    return arr


def createPodTest(arr, schedulerName):
    start_time = datetime.datetime.now()
    for i in range(0, len(arr)):
        k8sOperater.createTestPod(i, arr[i], schedulerName)
    end_time = datetime.datetime.now()


def addNum():
    global testNum
    testNum = testNum + 1


def multiNum():
    global testNum
    testNum = testNum * 2


if __name__ == '__main__':
    arr = np.array([1.2, 1.1, 3.1], dtype='float32')
    b = arr.astype('int')
    print(b.dtype)
    # glob_dict.set_value("num", 1)
    # glob_dict.set_value("num", glob_dict.get_value("num")+1)
    # addNum()
    # multiNum()
    # qValues = np.float32(np.array([0] * 3))
    # print(glob_dict.get_value("num"))
