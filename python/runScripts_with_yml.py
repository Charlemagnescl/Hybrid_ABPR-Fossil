import os
import sys
import threading
import datetime
import time
import yaml
import argparse
import subprocess
from reprint import output

# load arg parser
parser = argparse.ArgumentParser(description="run script with json config file")
parser.add_argument('--fnRunConfig', type=str, required=True)

# global parameters
fnRunConfig = './runConfig.yml'
Max_threads = 8
dnScripts = './Scripts/'
runnable_file_suffix = '.bat'
Config = {}
mutex = threading.Lock()
Finished_Threads = 0
Total_Threads = 0


# 
def execCmd(cmd, output_lines, result_list):
    # 
    global mutex, Finished_Threads

    #
    tid = threading.get_native_id()
    mutex.acquire()
    output_lines[format_tid(tid)] = 'cmd is ' + cmd.split('>')[0]
    mutex.release()

    #
    ret = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #
    mutex.acquire()
    if format_tid(tid) not in result_list.keys():
        output_lines.pop(format_tid(tid))
        if ret.returncode == 0:
            if 'Success threads' not in output_lines.keys():
                output_lines['Success threads'] = 0
            else:
                output_lines['Success threads'] += 1
            result_list[format_tid(tid)] = ' Success. ' + str(ret) 
        else:
            if 'Error threads' not in output_lines.keys():
                output_lines['Error threads'] = 0
            else:
                output_lines['Error threads'] += 1
            result_list[format_tid(tid)] = ' Error. ' + str(ret) 
    Finished_Threads += 1
    progress = Finished_Threads / Total_Threads
    output_lines['Progress'] = "[{done}{padding}] {percent}%".format(
                    done = "#" * int(progress*10),
                    padding = " " * (10 - int(progress*10)),
                    percent = int(progress*100)
                    )
    mutex.release()

#
def loadConfig():
    # 
    global Max_threads, dnScripts, Config

    if 'Max_threads' in Config:
        Max_threads = Config['Max_threads']
    if 'dnScripts' in Config:
        dnScripts = Config['dnScripts']


def main():
    # global parameters
    global fnRunConfig, fnRunConfig, Config, Total_Threads

    # parse arguments
    args = parser.parse_args()
    fnRunConfig = args.fnRunConfig

    # load yml config
    with open(fnRunConfig, 'r') as f:
        Config = yaml.safe_load(f)
    print(Config)

    # update default config with runConfig yaml
    loadConfig()

    #
    cur_path = dnScripts
    file_list = os.listdir(cur_path)
    
    #
    cmds = []
    for file_name in file_list: 
        if file_name.endswith(runnable_file_suffix):
            #print(cur_path + file_name)
            cmds.append(cur_path + file_name)
    Total_Threads = len(cmds)
    
    #
    threads = []
    result_list = {}
    print('cwd: ' + os.getcwd())
    print("all scripts begin %s" % (datetime.datetime.now()))
    with output(output_type='dict') as output_lines:

        #
        progress = Finished_Threads / Total_Threads
        output_lines['Progress'] = "[{done}{padding}] {percent}%".format(
                        done = "#" * int(progress*10),
                        padding = " " * (10 - int(progress*10)),
                        percent = int(progress*100)
                        )

        for cmd in cmds:  

            #
            while threading.active_count() > Max_threads:
                output_lines['active_Threads'] = threading.active_count()
                time.sleep(1)
            
            #
            th = threading.Thread(target=execCmd, args=(cmd, output_lines ,result_list)) 
            th.start()       
            threads.append({'id': th.native_id ,'thread': th, 'cmd': cmd})
        # 
        for each in threads:
            th = each['thread']
            th.join()  

    print("all scripts end%s" % (datetime.datetime.now()))
    for each in result_list:
        print(each, result_list[each])
    

def format_tid(tid):
    if not isinstance(tid, str):
        return 'Thread-' + str(tid)
    else:
        return 'Thread-' + tid


if __name__ == "__main__":
    main()  #https://www.jianshu.com/p/ba56192002c8

