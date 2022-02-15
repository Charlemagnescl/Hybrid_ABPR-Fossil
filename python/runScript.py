import os
import sys
import threading
import datetime
import time



def execCmd(cmd):
        print("script %s begin %s" % (cmd, datetime.datetime.now() ))
        os.system(cmd)
        print("script %s end %s" % (cmd, datetime.datetime.now()))


def run():
    dataset = 'ML100K'
    istest = False
    if(len(sys.argv) > 1):
        k = 1
        while(k < len(sys.argv)):
            if sys.argv[k] == '-data':
                dataset = sys.argv[k+1]
            if sys.argv[k] == '-istest':
                if sys.argv[k+1] == 'test':
                    istest = True
            k = k+2

    cur_path = os.path.dirname(os.path.realpath(__file__))
    if istest:
        cur_path = cur_path + '\\python\\' + dataset + 'test' + '\\'
    else:
        cur_path = cur_path + '\\python\\' + dataset + '\\'
    file_list = os.listdir(cur_path)
    #print('cur path = ' + cur_path)
    cmds = []
    for file_name in file_list: 
        #print(file_name) 
        if file_name.startswith('Script') and file_name.endswith('.bat'):
            # print(file_name)
            cmds.append(cur_path + file_name)
    threads = []
    print("all scripts begin%s" % (datetime.datetime.now()))
    for cmd in cmds:    
        while threading.active_count() > 100:
            time.sleep(20000)
        th = threading.Thread(target=execCmd, args=(cmd,)) 
        th.start()       
        threads.append(th)

    for th in threads:
        th.join()       

    print("all scripts end%s" % (datetime.datetime.now()))



if __name__ == "__main__":
    run()  #https://www.jianshu.com/p/ba56192002c8

