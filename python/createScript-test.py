import os
import sys
from pathlib import Path

def mymap(x):
    return x / 10.0

def getBestConfig(dataset):
    curdir = os.getcwd()
    
    workdir = curdir.replace('\\python', '\\result')
    print('workdir : ' + workdir)
    os.chdir(workdir)
    resultraw = os.popen('python .\\bestResult_valid.py')

    rawtext = resultraw.readlines()

    para = ''
    for line in rawtext:
        line.rstrip('\n')
        if line != '':
            print(line)
        if line.startswith('best para:'):
            para = line.split(': ')[1]

    os.chdir(curdir)

    if(para == ''):
        print('best para not found!')
        exit(1)
    
    return para

def parsePara(Dataset, file_name):
    print('parse para : ' + str(file_name))

    if(not str(file_name).startswith(Dataset + 'valid')):
        print('wrong file name format!')
        exit(1)
    
    file_name = file_name.rstrip('.txt\n')
    regs = file_name.split('-')[1:]
    rregs = {}

    for reg in regs:
        if reg.startswith('nt'):
            rregs['nt'] = float(reg.replace('nt_', ''))
        if reg.startswith('L'):
            rregs['L'] = int(reg.replace('L_', ''))
        if reg.startswith('T'):
            rregs['T'] = int(reg.replace('T_',''))
        if reg.startswith('eta_g'):
            rregs['eta_g'] = float(reg.replace('eta_g_','')) 

    if len(rregs) < 4:
        print('len of regs wrong !')
        exit(1)
    
    return rregs

def getTargetDataSet():
    dataset = 'ML100K'
    if len(sys.argv) > 2:
        k = 1
        while k + 1 < len(sys.argv):
            if sys.argv[k] == '-dataset':
                dataset = sys.argv[k+1]

    print('using dataset : ' + dataset)
    return dataset


def createScript():
    program = 'java'
    code_name = 'Main'

    dataset = getTargetDataSet()
    regs = parsePara(dataset, getBestConfig(dataset))    
    print('regs : ' + str(regs))

    dimension = 20
    SizeOfGroup = 3
    gamma = 0.01
    
    # print(eta_g)
    #data_set = ['ML1M', 'ML100K','Office','Cell','Auto','Video']


    # count_of_data_set = {
    #     'ML1M':['6040', '3952'],
    #     'ML100K':['943', '1682'],
    #     'Office':['16243','5526'],
    #     'Cell':['67453','17969'],
    #     'Auto':['31877','9992'],
    #     'Video':['30935','12111']        
    # }
    count_of_data_set = {
        'ML100K':['943', '1682'],  
    }
    # #num_iterations = ['1000']
    # num_iterations_perTest = '10'
    topK = '20'
    #result_file_set = ['Result-ML1M', 'Result-ML100K','Result-Office','Result-Cell', 'Result-Auto', 'Result-Video']
    result_file_set = ['Result-ML100K']

    fnTrainData_set = '..\\data\\' + dataset + '\\' +'train.csv'
    fnTestData_set = '..\\data\\' + dataset + '\\' +'test.csv'

    
    n = count_of_data_set[dataset][0]
    m = count_of_data_set[dataset][1]
    fnTrainData = fnTrainData_set
    fnTestData = fnTestData_set
    file_name_begin = 'Script-test-' + dataset
    result_file_name_begin ='.\\result\\' + result_file_set[0]+'\\' +dataset+'test'

    p = Path(dataset + 'test')
    p.mkdir(exist_ok=True)

    total_count = 3
    for i in range(total_count):
        para ='-nt_'+str(regs['nt'])+\
        '-L_'+str(regs['L'])+\
        '-T_'+str(regs['T'])+\
        '-eta_g_'+ str(regs['eta_g'])
        file_name = dataset + 'test' +'/'+file_name_begin + para+str(i) + '.bat'
        with open(file_name, "w") as f:
            line = program +' '+\
            code_name+' '+\
            '-fnTrainData '+fnTrainData+' '+\
            '-fnTestData '+fnTestData+' '+\
            '-n '+str(n)+' '+\
            '-m '+str(m)+' '+\
            '-alpha_w '+str(regs['nt'])+' '+\
            '-alpha_v '+str(regs['nt'])+' '+\
            '-beta_v '+str(regs['nt'])+' '+\
            '-beta_eta '+str(regs['nt'])+' '+\
            '-L '+str(regs['L'])+' '+\
            '-gamma '+str(gamma)+' '+\
            '-T '+str(regs['T'])+' '+\
            '-topK '+str(topK)+' '+\
            '-d ' + str(dimension) + ' ' + \
            '-SizeOfGroup ' + str(SizeOfGroup) + ' ' + \
            '-eta_g ' + str(regs['eta_g']) + ' ' + \
            '> '+result_file_name_begin+\
            para+str(i) +\
            '.txt'
            f.write(line+'\n\n')
        f.close()

        

if __name__ == "__main__":
    createScript()