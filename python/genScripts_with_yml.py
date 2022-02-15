import yaml
import subprocess
import sys
import os
import argparse

# load arg parser
parser = argparse.ArgumentParser(description="Generate scripts with json config")
parser.add_argument('--fnConfig', type=str, default='./ScriptConfig.yml')
parser.add_argument('--multiple-test', type=bool, default=False)

# global parameters
keys = []
scripts = []
config = {}
dnScripts = './Scripts/'
dnOutResults = './results/'

# entrance
def main():
    global config
    # parse args
    args = parser.parse_args()

    # load json config file
    with open(args.fnConfig, 'r') as f:
        config = yaml.safe_load(f)
    
    # some configurations
    configuration()

    # gen scripts
    generate_Scripts()

# load configurations
def configuration():
    global keys, dnScripts, dnOutResults
    keys = list(config.keys())
    if keys.count('dnScripts') > 0:
        dnScripts = config['dnScripts']
    if keys.count('dnOutResult') > 0:
        dnOutResults = config['dnOutResults']

# generate scripts with configurations given by json
def generate_Scripts():

    fileName = config['name']
    keys.remove('name')
    cmd = config['runCmd']
    keys.remove('runCmd')

    complete_fileName(cur_key_id=0, fileName=fileName, cmd = cmd)

# dfs to complete file name and cmds
def complete_fileName(cur_key_id, fileName, cmd):
    if(cur_key_id >= len(keys)):
        fileName = fileName + '.bat'
        cmd = cmd + ' > ' + dnOutResults + fileName.replace('bat', 'txt')
        with open(dnScripts + fileName, 'w') as f:
            f.write(cmd)
        return
    
    key = keys[cur_key_id]
    values = config[key]

    if isinstance(values, list):
        for value in values:
            complete_fileName(cur_key_id=cur_key_id+1, 
                                fileName=format_fileName(fileName, key, value), cmd = format_cmd(cmd, key, value))
    else:
        complete_fileName(cur_key_id=cur_key_id+1, 
                            fileName=format_fileName(fileName, key, values), cmd = format_cmd(cmd, key, values))


def format_fileName(fileName, key, value):
    # preprocess the float or int into str
    if isinstance(value, float):
        value = str(value).replace('.', '_')
    elif isinstance(value, int):
        value = str(value)
    
    # retain file name only.
    if value.count('/') >= 1:
        value = value.split('/')[-1].split('.')[0]
    
    if fileName == '':
        return fileName + str(key) + "_" + value
    else:
        return fileName + "_" + str(key) + "_" + value

def format_cmd(cmd, key, value):
    # 
    value = str(value)
    cmd = cmd + ' -' + key + ' ' + value
    return cmd

if __name__ == "__main__":
    main()