from distutils.log import error
import argparse
import textwrap
import yaml
from concurrent.futures import thread
import os
import sys
import threading
import datetime
import time
import platform
import argparse
import subprocess
from reprint import output
import timeit

# ========================================================================================================================================================
# Custom Errors
# ========================================================================================================================================================
class ConfigError(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) # initialize super class
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo


# ========================================================================================================================================================
# Result analyse
# ========================================================================================================================================================

class ResultAnalyser(object):
    # class parameters
    dnResults = 'result/ml-100k'
    dnAnalysis = 'Analysis/ml-100k'
    focus_Paramter_names = ['tradeoff']
    focus_Metric_names = ['NDCG@20']
    REQUIRED_CONFIG = ['dnResult', 'dnAnalysis', 'focus_Paramter_names', 'focus_Metric_names']
    Config = {}

    # init
    def __init__(self, config):
        self.Config = config
        try:
            self.dnResults = self.Config['Global']['dnResults']
            self.dnAnalysis = self.Config['Global']['dnAnalysis']
            self.focus_Metric_names = self.Config['Analysis']['focus_Metric_names']
            self.focus_Paramter_names = self.Config['Analysis']['focus_Paramter_names']
        except Exception:
            print('{required_config} is missing in config file !' .format(required_config=str(self.REQUIRED_CONFIG) ))
            sys.exit(1)

    # compare to str.isnumeric(), this method could distinguish float type number from string.
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass
    
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
    
        return False

    # type: func
    # input: name of directory to walk
    # output name of files in target directory
    def get_files(self, dir_name):

        def format_path(cur_file_name):
            return os.path.join( os.path.dirname( __file__ ), dir_name, cur_file_name ).replace('\\', '/')  # windows specific

        file_list = os.listdir(dir_name)

        return list(map(format_path, file_list))

    # fileName format: ..._parameterName_parameterValue_...
    def getParameterValue_byName(self, fileName, parameterName):
        parameters = fileName.rstrip('.txt').split('_')
        p_position = parameters.index(parameterName)

        #
        if p_position + 2 < len(parameters) and parameters[p_position+2].isnumeric():
            p_value = float(parameters[p_position+1] + '.' + parameters[p_position+2])
        else:
            p_value = int(parameters[p_position+1])

        return p_value

    def counting(self,file_list):

        # init
        result = {}
        for p_name in self.focus_Paramter_names:
            result[p_name] = {}
            for file in file_list:
                cur_p_value = self.getParameterValue_byName(file, p_name)
                result[p_name][cur_p_value] = {}
                for metric_name in self.focus_Metric_names:
                    count = 0
                    metric_value = 0.0
                    for file in file_list:
                        
                        p_value = self.getParameterValue_byName(file,p_name)
                        if p_value == cur_p_value:
                            extract_metric_value = 0.0
                            # init
                            with open(file, 'r') as f:
                                for line in f:
                                    if line.startswith(metric_name):
                                        extract_metric_value = float(line.split(':')[-1])
                            count += 1
                            metric_value += extract_metric_value
                    
                    #
                    result[p_name][cur_p_value][metric_name] = metric_value / count 
        
        print(result)
                
                

    def analyse(self):

        #
        file_list = self.get_files(self.dnResults)

        #
        self.counting(file_list)

# ========================================================================================================================================================
# Run Scripts
# ========================================================================================================================================================


class ScriptRunner(object):
    # The multiprocess code is referenced from https://www.jianshu.com/p/ba56192002c8
    
    # class parameters
    fnRunResult = 'runResult.txt'
    Max_threads = 8
    dnScripts = './Scripts/'
    runnable_file_suffix = '.bat'
    Config = {}
    mutex = threading.Lock()
    Finished_Threads = 0
    Total_Threads = 1
    terminal = output()
    notCompile = True


    # init
    def __init__(self, config, not_compile):
        self.Config = config
        self.mutex = threading.Lock()
        self.notCompile = not_compile


    # 
    def execCmd(self,cmd, output_lines, result_list):
        # ========================================================================================
        #
        tid = threading.get_native_id()
        self.mutex.acquire()
        output_lines[self.format_tid(tid)] = 'cmd is ' + cmd.split('>')[0]
        self.mutex.release()

        # ========================================================================================
        #
        time1 = timeit.default_timer()
        ret = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd())
        time2 = timeit.default_timer()

        # ========================================================================================
    
        self.mutex.acquire()
        if self.format_tid(tid) not in result_list.keys():
            output_lines.pop(self.format_tid(tid))
            if ret.returncode == 0:
                if 'Success threads' not in output_lines.keys():
                    output_lines['Success threads'] = 0
                else:
                    output_lines['Success threads'] += 1
                result_list[self.format_tid(tid)] = (ret, str('Cost {Time_Consuming} min' .format( Time_Consuming= str((time2 - time1)/60) ) ) ) 
            else:
                if 'Error threads' not in output_lines.keys():
                    output_lines['Error threads'] = 0
                else:
                    output_lines['Error threads'] += 1
                result_list[self.format_tid(tid)] = ret
        self.Finished_Threads += 1

        self.update_ProgressBar()
        self.mutex.release()
        # ========================================================================================


    #
    def loadConfig(self):

        if 'Max_threads' in self.Config['Run']:
            self.Max_threads = self.Config['Run']['Max_threads']
        if 'dnScripts' in self.Config['Global']:
            self.dnScripts = self.Config['Global']['dnScripts']
        if 'fnRunResult' in self.Config['Run']:
            self.fnRunResult = self.Config['Run']['fnRunResult']
        if 'runnable_file_suffix' in self.Config['Global']:
            self.runnable_file_suffix = self.Config['Global']['runnable_file_suffix']
        
        if not self.notCompile:
            if 'compileCommend' not in self.Config['Global']:
                try:
                    raise ConfigError('Config Error, compile commend needed !')
                except ConfigError as e:
                    print(e)
                    sys.exit(1)
            else:
                ret = subprocess.run(self.Config['Global']['compileCommend'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd())
                if ret.returncode == 0:
                    print('Compile commend \'{compileCommend}\' success !' .format(compileCommend=self.Config['Global']['compileCommend']))
                else:
                    print('Compile commend \'{compileCommend}\' fail !' .format(compileCommend=self.Config['Global']['compileCommend']))
                    try:
                        raise Exception()
                    except Exception as e:
                        print('Compile commend \'{compileCommend}\' fail !' .format(compileCommend=self.Config['Global']['compileCommend']))
                        sys.exit(1)
        


    def run(self):
        # update default config with runConfig yaml
        self.loadConfig()

        # ========================================================================================
        cur_path = self.dnScripts
        file_list = os.listdir(cur_path)
        # print(file_list)
        # ========================================================================================


        # ========================================================================================
        cmds = []
        for file_name in file_list: 
            # print(file_name)
            if file_name.endswith(self.runnable_file_suffix):
                if self.runnable_file_suffix == 'bat':
                    cmds.append( os.path.join(os.getcwd(), cur_path, file_name).replace('\\', '/') ) # windows case
                elif self.runnable_file_suffix == 'sh':
                    cmds.append( 'sh ' + os.path.join( os.getcwd(), cur_path, file_name ) ) # linux case
        self.Total_Threads = len(cmds)
        # ========================================================================================
        
        #
        threads = []
        result_list = {}
        print('cwd: ' + os.getcwd())

        if self.Total_Threads == 0:
            print('Error! No script to be run ! Check your configuration files ! ')
            sys.exit(1)

        print('{threads_num} Scripts to be run ! Sample cmd : {sampleCmd}' .format(threads_num=len(cmds), sampleCmd=cmds[0] ) )
        
        # ========================================================================================

        with output(output_type='dict') as self.terminal:

            #
            self.update_ProgressBar()

            # ====================================================================================
            for cmd in cmds:  
                #
                while threading.active_count() >= self.Max_threads:
                    self.terminal['active_Threads'] = threading.active_count()
                    time.sleep(1)
                
                #
                th = threading.Thread(target=self.execCmd, args=(cmd, self.terminal ,result_list)) 
                th.start()       
                threads.append({'id': th.native_id ,'thread': th, 'cmd': cmd})
            # 
            for each in threads:
                th = each['thread']
                th.join()  

            # ====================================================================================
        # ========================================================================================


        print("all scripts end%s" % (datetime.datetime.now()))
        print('Run result stored at {fnRunResult}' .format(fnRunResult = self.fnRunResult))
        
        
        dir_name = os.path.dirname(self.fnRunResult)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        with open(self.fnRunResult, 'w') as f:
            for each in result_list.keys():
                if not isinstance(result_list[each], tuple):
                    f.write(str(each) + ': ' + str(result_list[each].returncode) + '\n')
                    f.write('\t args: ' + str(result_list[each].args) + '\n')
                    f.write('\t stdout: ' + str(result_list[each].stdout.decode('gbk')) + '\n')
                    f.write('\t stderr: ' + str(result_list[each].stderr.decode('gbk')) + '\n\n')
                else:
                    f.write(str(each) + ': ' + str(result_list[each][0].returncode) + '\n')
                    f.write('\t args: ' + str(result_list[each][0].args) + '\n')
                    f.write('\t stdout: ' + str(result_list[each][0].stdout.decode('gbk')) + '\n')
                    f.write('\t stderr: ' + str(result_list[each][0].stderr.decode('gbk')) + '\n')
                    f.write('\t ' + str(result_list[each][1]) + '\n\n')
    

    # 
    def update_ProgressBar(self):
        progress = self.Finished_Threads / self.Total_Threads
        self.terminal['Progress'] = "[{done}{padding}] {percent}%".format(
                        done = "#" * int(progress*10),
                        padding = " " * (10 - int(progress*10)),
                        percent = int(progress*100)
                        )

    #
    def format_tid(self, tid):
        if not isinstance(tid, str):
            return 'Thread-' + str(tid)
        else:
            return 'Thread-' + tid

# ========================================================================================================================================================
# Generate Scripts
# ========================================================================================================================================================

class ScriptGenerator(object):
    # class parameters
    config = {}
    keys = []
    scripts = []
    config = {}
    dnScripts = './Scripts/'
    dnResults = './results/'
    runnable_file_suffix = '.bat'
    result_file_suffix = '.txt'

    # init
    def __init__(self, config):
        self.config = config
        

    # entrance
    def generate(self):    
        # load script config
        self.keys = list(self.config['Script'].keys())
        
        
        # some configurations
        self.loadConfig()

        # gen scripts
        self.generate_Scripts()

    # load configurations
    def loadConfig(self):
        
        if 'dnScripts' in self.config['Global']:
            self.dnScripts = self.config['Global']['dnScripts']
        if 'dnResults' in self.config['Global']:
            self.dnResults = self.config['Global']['dnResults']
        if 'runnable_file_suffix' in self.config['Global']:
            self.runnable_file_suffix = self.config['Global']['runnable_file_suffix']
        if 'result_file_suffix' in self.config['Global']:
            self.result_file_suffix = self.config['Global']['result_file_suffix']
        
        print( 'dnScripts: {dnScripts} \ndnResults: {dnOutResults}' .format( dnScripts=self.dnScripts, dnOutResults=self.dnResults ) )

    # generate scripts with configurations given by json
    def generate_Scripts(self):

        fileName = self.config['Global']['name']
        cmd = self.config['Global']['runCmd']

        self.complete_fileName(cur_key_id=0, fileName=fileName, cmd = cmd)

    # dfs to complete file name and cmds
    def complete_fileName(self,cur_key_id, fileName, cmd):
        if(cur_key_id >= len(self.config['Script'])):
            fileName = fileName + '.' + self.runnable_file_suffix
            cmd = cmd + ' > ' + self.dnResults + fileName.replace(self.runnable_file_suffix, self.result_file_suffix)
            if not os.path.exists(self.dnScripts):
                os.makedirs(self.dnScripts)
            with open(self.dnScripts + fileName, 'w') as f:
                # print(dnScripts + fileName)
                f.write(cmd)
            return
        
        key = self.keys[cur_key_id]
        values = self.config['Script'][key]
        if isinstance(values, dict):
            key = values['keys']
            values = values['values']

        if isinstance(values, list):
            for value in values:
                self.complete_fileName(cur_key_id=cur_key_id+1, 
                                    fileName=self.format_fileName(fileName, key, value), cmd = self.format_cmd(cmd, key, value))
        else:
            self.complete_fileName(cur_key_id=cur_key_id+1, 
                                fileName=fileName, cmd = self.format_cmd(cmd, key, values))


    def format_fileName(self, fileName, key, value):
        # preprocess the float or int into str
        if isinstance(value, float):
            value = str(value).replace('.', '_')
        elif isinstance(value, int):
            value = str(value)
        
        # retain file name only.
        if value.count('/') >= 1:
            value = value.split('/')[-1].split('.')[0]
        

        if isinstance(key, list):
            for k in key:
                if fileName == '':
                    fileName = fileName + str(k) + "_" + value
                else:
                    fileName = fileName + "_" + str(k) + "_" + value
        else:
            if fileName == '':
                fileName = fileName + str(key) + "_" + value
            else:
                fileName = fileName + "_" + str(key) + "_" + value
        
        return fileName

    def format_cmd(self, cmd, key, value):
        # 
        value = str(value)
        if isinstance(key, list):
            for k in key:
                cmd = cmd + ' -' + k + ' ' + value
        else:
            cmd = cmd + ' -' + key + ' ' + value
        return cmd



# ========================================================================================================================================================
# Commendline Tool
# ========================================================================================================================================================

class CommendLine(object):
    #
    Config = {}
    Args = {}

    # 
    def __init__(self):
        self.parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Commendline Tool for easily run experiments.")
        self.parser.add_argument('-nc', '--not-compile', help='Not complie before run', action="store_true")

        self.parser.add_argument('-c', '--fnconfig', type=str, required=True, help='path to yaml config file')

        modeHelp = {
            'genName': 'gen',
            'genHelp': 'Generate Scripts only',
            'runName': 'run',
            'runHelp': 'Run Scripts only',
            'anaName': 'ana',
            'anaHelp': 'Analyse result only',
            'genAndrun': 'genAndrun',
            'genAndrunHelp': 'Generate and run Scripts',
            'runAndana': 'runAndana',
            'runAndanaHelp': 'Run Scripts and analyse them',
            'all': 'all',
            'allHelp': 'Generate and run Scripts and then analyse the result'
        }
        self.parser.add_argument('-m', '--mode', type=str, required=True,
        choices= ['gen', 'run', 'ana', 'genAndrun', 'runAndana', 'all'],
        help=textwrap.dedent('''\
        {genName}: {genHelp}; 
        {runName}: {runHelp}; 
        {anaName}: {anaHelp}; 
        {genAndrun}: {genAndrunHelp}; 
        {runAndana}: {runAndanaHelp}; 
        {all}: {allHelp}'''
            .format(genName=modeHelp['genName'], genHelp=modeHelp['genHelp'], runName=modeHelp['runName'], runHelp=modeHelp['runHelp'], anaName=modeHelp['anaName'], anaHelp=modeHelp['anaHelp'], genAndrun=modeHelp['genAndrun'],
            genAndrunHelp=modeHelp['genAndrunHelp'], runAndana=modeHelp['runAndana'], runAndanaHelp=modeHelp['runAndanaHelp'], all=modeHelp['all'], allHelp=modeHelp['allHelp'])) )

    def begin(self):
        #
        self.Args = self.parser.parse_args()
        # print(self.Args.not_compile)
        
        #
        fnConfig = self.Args.fnconfig
        with open(fnConfig, 'r') as f:
            self.Config = yaml.safe_load(f)
        
        # print(self.Config)
        
        self.do()
    
    def do(self):
        mode = self.Args.mode
        if mode == 'gen':
            generator = ScriptGenerator(self.Config)
            generator.generate()
        elif mode == 'run':
            runner = ScriptRunner(self.Config, self.Args.not_compile)
            runner.run()
        elif mode == 'ana':
            analyser = ResultAnalyser(self.Config)
            analyser.analyse()
        elif mode == 'genAndrun':
            generator = ScriptGenerator(self.Config)
            generator.generate()

            runner = ScriptRunner(self.Config, self.Args.not_compile)
            runner.run()
        elif mode == 'runAndana':
            runner = ScriptRunner(self.Config)
            runner.run()

            analyser = ResultAnalyser(self.Config)
            analyser.analyse()
        elif mode == 'all':
            generator = ScriptGenerator(self.Config)
            generator.generate()

            runner = ScriptRunner(self.Config, self.Args.not_compile)
            runner.run()

            analyser = ResultAnalyser(self.Config)
            analyser.analyse()

if __name__ == '__main__':
    commendline = CommendLine()
    commendline.begin()