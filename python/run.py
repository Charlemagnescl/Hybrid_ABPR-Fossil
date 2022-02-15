import subprocess
import sys
import os

def main():

    dataPath = './Data-S-FMSM/Data-S-FMSM/'
    outPath = './python/out/'

    chosenDataset = 'ML100K'
    isTest = "False"

    configFilePath = './ps1/'
    if (len(sys.argv) > 1):
        k = 1
        
        while k + 1 < len(sys.argv):
            print(sys.argv[k])
            print(sys.argv[k+1])
            if sys.argv[k] == '-data':
                chosenDataset = sys.argv[k+1]
            if sys.argv[k] == '-config':
                configFilePath = sys.argv[k+1]
            if sys.argv[k] == '-isTest':
                isTest = sys.argv[k+1]
            k += 2

    if isTest == 'False':
        Train(dataPath, outPath, chosenDataset)
    else:
        Test(dataPath, outPath, chosenDataset)
        
        
    
    
def Train(dataPath, outPath, chosenDataset):
    regulazationTerm = [0.001, 0.01, 0.1]
    L = [1,2,3]
    T = [100, 500, 1000]



    print('chosenDataset: ' + chosenDataset)
    
    configfile = './ps1/config_' + chosenDataset + '.txt'

    print('configFile: ' + configfile)

    n = 0
    m = 0
    gamma = 0.0
    topk = 0
    d = 0
    SizeOfGroup = 0

    with open(configfile) as f:
        for line in f:
            cline = line.split(' ')
            if cline[0] == 'n:':
                n = int(cline[1])
            if cline[0] == 'm:':
                m = int(cline[1])
            if cline[0] == 'gamma:':
                gamma = float(cline[1])
            if cline[0] == 'topk:':
                topk = int(cline[1])
            if cline[0] == 'd:':
                d = int(cline[1])
            if cline[0] == 'SizeofGroup:':
                SizeOfGroup = int(cline[1])
    
    trainPath = findFile( [chosenDataset, 'train'], dataPath)
    validPath = findFile( [chosenDataset, 'valid'], dataPath)
    testPath = findFile( [chosenDataset, 'test'] , dataPath)

    subprocess.Popen('javac Main.java').wait()

    
    for re in regulazationTerm:
        for t in T:
            for l in L:
                storePath = outPath + chosenDataset + '/' + 'train_' + 'R' + str(re) + '_T' + str(t) + '_L' + str(l) + 'f.txt'
                if SizeOfGroup != 0:
                    command = 'java Main -fnTrainData ' + trainPath + ' -fnTestData ' + validPath + ' -n ' + str(n) + ' -m ' + str(m) + ' -alpha_w ' + str(re) + ' -alpha_v ' + str(re) + ' -beta_v ' + str(re) + ' -beta_eta ' + str(re) + ' -L ' + str(l) + ' -gamma ' + str(gamma) + ' -T ' + str(t) + ' -topK ' + str(topk) + ' -d ' + str(d) + ' -SizeOfGroup ' + str(SizeOfGroup) +  ' > ' + storePath
                else:
                    command = 'java Main -fnTrainData ' + trainPath + ' -fnTestData ' + validPath + ' -n ' + str(n) + ' -m ' + str(m) + ' -alpha_w ' + str(re) + ' -alpha_v ' + str(re) + ' -beta_v ' + str(re) + ' -beta_eta ' + str(re) + ' -L ' + str(l) + ' -gamma ' + str(gamma) + ' -T ' + str(t) + ' -topK ' + str(topk) + ' -d ' + str(d)  + ' > ' + storePath
                
                with open('./' + chosenDataset + '_' + 'R' + str(re) + '_T' + str(t) + '_l' + str(l) + '.bat', 'w') as f:
                    f.write(command)
                    f.write('\npause')

def Test(dataPath, outPath, chosenDataset):
    testPath = findFile( [chosenDataset, 'test'] , dataPath)
    trainPath = findFile( [chosenDataset, 'train'], dataPath)

    print('chosenDataset: ' + chosenDataset)
    
    configfile = './ps1/config_' + chosenDataset + '_test.txt'

    print('configFile: ' + configfile)

    SizeOfGroup = 0

    with open(configfile) as f:
        for line in f:
            cline = line.split(' ')
            if cline[0] == 'n:':
                n = int(cline[1])
            if cline[0] == 'm:':
                m = int(cline[1])
            if cline[0] == 'gamma:':
                gamma = float(cline[1])
            if cline[0] == 'topk:':
                topk = int(cline[1])
            if cline[0] == 'd:':
                d = int(cline[1])
            if cline[0] == 'SizeofGroup:':
                SizeOfGroup = int(cline[1])
            if cline[0] == 'L:':
                L = int(cline[1])
            if cline[0] == 'T:':
                T = int(cline[1])
            if cline[0] == 'rt:':
                rt = float(cline[1])
            
    for i in range(3):
        storePath = outPath + chosenDataset + '/' + 'train_' + 'R' + str(rt) + '_T' + str(T) + '_L' + str(L) + '_test_' + str(i) + '.txt'
        if SizeOfGroup != 0:
            command = 'java Main -fnTrainData ' + trainPath + ' -fnTestData ' + testPath + ' -n ' + str(n) + ' -m ' + str(m) + ' -alpha_w ' + str(rt) + ' -alpha_v ' + str(rt) + ' -beta_v ' + str(rt) + ' -beta_eta ' + str(rt) + ' -L ' + str(L) + ' -gamma ' + str(gamma) + ' -T ' + str(T) + ' -topK ' + str(topk) + ' -d ' + str(d) + ' -SizeOfGroup ' + str(SizeOfGroup) +  ' > ' + storePath
        else:
            command = 'java Main -fnTrainData ' + trainPath + ' -fnTestData ' + testPath + ' -n ' + str(n) + ' -m ' + str(m) + ' -alpha_w ' + str(rt) + ' -alpha_v ' + str(rt) + ' -beta_v ' + str(rt) + ' -beta_eta ' + str(rt) + ' -L ' + str(L) + ' -gamma ' + str(gamma) + ' -T ' + str(T) + ' -topK ' + str(topk) + ' -d ' + str(d)  + ' > ' + storePath
        
        with open('./' + chosenDataset + '_' + 'R' + str(rt) + '_T' + str(T) + '_l' + str(L) + '_test' + str(i) + '.bat', 'w') as f:
            f.write(command)
            f.write('\npause')


    
def findFile(target, curDir):
    try:
        dirs = os.listdir(curDir)
    except NotADirectoryError or FileNotFoundError:
        flag = True
        for tar in target:
            if curDir.find(tar) == -1:
                flag = False
        if flag:
            return curDir.rstrip('/')
        else:
            return ''


    filepath = ''
    for di in dirs:
        
        filepath = findFile(target, curDir + di + '/')
        if filepath != '' :
            return filepath
    
    return filepath

if __name__ == "__main__":
    main()    
