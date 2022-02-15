import os
import shutil
from pathlib import Path

def mymap(x):
    return x / 10.0



def createScript():
    program = 'java'
    code_name = 'Main'


    # dimension = ['50', '100', '150','200']

    dimension = ['20']
    nt = ['0.001']
    L = ['3']
    SizeOfGroup = 3
    gamma = 0.01
    T = ['1000']
    
    # etag = list(range(1,10))
    etag = [1]
    # print(eta_g)
    #data_set = ['ML1M', 'ML100K','Office','Cell','Auto','Video']
    data_set = ['ML100K']


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
        'Office':['16243','5526']     
    }
    #num_iterations = ['1000']
    num_iterations_perTest = '10'
    topK = '20'
    #result_file_set = ['Result-ML1M', 'Result-ML100K','Result-Office','Result-Cell', 'Result-Auto', 'Result-Video']
    result_file_set = ['Result-ML100K']

    # clustering
    # K4clustering = [10,30,50,70,90,120]
    p4clustering = [0.0,0.3,0.5,0.8,1.0]

    # Most Similar user size
    SimUserSize = [10, 30, 50, 70, 100, 300]

    fnTrainData_set = {}
    fnTestData_set = {}
    for i in range(len(data_set)):
        fnTrainData_set[data_set[i]] = '..\\data\\' + data_set[i] + '\\' +'train.csv'
        fnTestData_set[data_set[i]] = '..\\data\\' + data_set[i] + '\\' +'valid.csv'

    for data_ID in range(len(data_set)):
        data = data_set[data_ID]
        n = count_of_data_set[data][0]
        m = count_of_data_set[data][1]
        fnTrainData = fnTrainData_set[data]
        fnTestData = fnTestData_set[data]
        file_name_begin = 'Script-valid-' + data
        result_file_name_begin ='.\\result\\' + result_file_set[data_ID]+'\\' +data+'valid'
 
        p = Path(data)
        shutil.rmtree('.\\' + data)
        p.mkdir(exist_ok=True)

        for nt_id in range(len(nt)):
            for L_id in range(len(L)):
                for T_id in range(len(T)):
                    for eta_g_id in range(len(etag)):
                        for s_id in range(len(SimUserSize)):
                            for p_id in range(len(p4clustering)):
                                para ='-nt_'+str(nt[nt_id])+\
                                '-L_'+str(L[L_id])+\
                                '-T_'+str(T[T_id])+\
                                '-eta_g_'+ str(etag[eta_g_id])+\
                                '-SimUserSize_'+str(SimUserSize[s_id])+\
                                '-p_'+str(p4clustering[p_id])
                                file_name = data+'/'+file_name_begin + para+'.bat'
                                with open(file_name, "w") as f:
                                    line = program +' '+\
                                    code_name+' '+\
                                    '-fnTrainData '+fnTrainData+' '+\
                                    '-fnTestData '+fnTestData+' '+\
                                    '-n '+str(n)+' '+\
                                    '-m '+str(m)+' '+\
                                    '-alpha_w '+str(nt[nt_id])+' '+\
                                    '-alpha_v '+str(nt[nt_id])+' '+\
                                    '-beta_v '+str(nt[nt_id])+' '+\
                                    '-beta_eta '+str(nt[nt_id])+' '+\
                                    '-L '+str(L[L_id])+' '+\
                                    '-gamma '+str(gamma)+' '+\
                                    '-T '+str(T[T_id])+' '+\
                                    '-topK '+str(topK)+' '+\
                                    '-d ' + str(dimension[0]) + ' ' + \
                                    '-SizeOfGroup ' + str(SizeOfGroup) + ' ' + \
                                    '-eta_g ' + str(etag[eta_g_id]) + ' ' + \
                                    '-SimUserSize ' + str(SimUserSize[s_id]) + ' ' + \
                                    '-p ' + str(p4clustering[p_id]) + ' ' + \
                                    '> '+result_file_name_begin+\
                                    para+\
                                    '.txt'
                                    f.write(line+'\n\n')
                                f.close()

        

if __name__ == "__main__":
    createScript()