import copy
import linecache
import os.path
import sys
from multiprocessing import Pool
#import fuzzyCal

from tqdm import trange

import FuzzyKnn
import Tool_io
import Tool_localization

# _formulaList={"crosstab", "dstar", "jaccard", "ochiai", "op2", "turantula"}
from Methods import machine_learning
from Sttaic_code_features import all_operators

_formulaList={"dstar", "jaccard", "ochiai"}
_CCstrategyList={"clean", "exchange", "relabel"}


def getSuspiciousnessFDistance(versionPath,covMatrix,inVector,formulaSus,use_list=None,baseline=True):
    print("模糊加权距离")
    if baseline:
        FD_All = Tool_io.checkAndLoad(versionPath[1], "data_FD_all")
        if FD_All != None:
            return FD_All
    FD_All = {}
    if baseline:
        for algorithm_k, algorithm_v in formulaSus.items():
            if algorithm_k == 'dstar':
            #if algorithm_k == 'dstar' or algorithm_k == 'dstar' or algorithm_k == 'dstar':
                FD = {}
                for case_index in trange(len(covMatrix)):
                    test = copy.deepcopy(covMatrix[case_index])
                    for key, value in formulaSus[algorithm_k]:
                        test[key] *= value
                    FD[case_index] = test
                FD_All[algorithm_k] = FD
        Tool_io.checkAndSave(versionPath[1], "data_FD_all", FD_All)
        print("FD end")
    return FD_All


def getSuspiciousnessScoreFactorSimple(versionPath,covMatrix,inVector,formulaSus_origin,use_list=None,baseline=True):
    print("SS start")
    formulaSus = formulaSus_origin
    SS_ALL_t = Tool_io.checkAndLoad(versionPath[1], "data_SS_all")
    if SS_ALL_t != None:
        # 原始SS特征维度
        origin_len = len(SS_ALL_t)
        # 怀疑度公式类型是否有增减
        formulaSus_copy = copy.deepcopy(formulaSus_origin)
        formulaSus,SS_ALL_t = Tool_io.add_del_formula(formulaSus_copy, SS_ALL_t)
        # 怀疑度公式与现有SS特征用到的怀疑度公式类型是否有减少
        now_len = len(SS_ALL_t)
        if now_len < origin_len:
            Tool_io.checkDele(versionPath[1], "data_SS_all")
            if len(formulaSus) == 0:
                Tool_io.checkAndSave(versionPath[1], "data_SS_all", SS_ALL_t)
                return SS_ALL_t
        if len(formulaSus) > 0:
            Tool_io.checkDele(versionPath[1], "data_SS_all")
        else:
            # 怀疑度公式与现有SS特征用到的怀疑度公式类型没有增加，原结果不变或删减后可直接返回
            return SS_ALL_t

    SS_ALL = {}
    if baseline:
        for algorithm_k, algorithm_v in formulaSus.items():
            SS = {}
            for case_index in trange(len(covMatrix)):
                if use_list == None or len(use_list) == 0 or case_index in use_list:
                #if inVector[case_index] == 0:
                    Sh_Num=0
                    Sh_Sum=0
                    Sl_Num=0
                    Sl_Sum=0
                    for key,value in formulaSus[algorithm_k]:
                        if covMatrix[case_index][key]==1:
                            if value>=0.5:
                                Sh_Num+=1
                                Sh_Sum+=value
                            else:
                                Sl_Num+=1
                                Sl_Sum+=value
                    if Sh_Num>0:
                        SS[case_index]=Sh_Sum/Sh_Num
                    else:
                        if Sl_Num == 0:
                            SS[case_index] = 0
                        else:
                            SS[case_index] = Sl_Sum / Sl_Num
            SS_ALL[algorithm_k] = SS

        # 若原结果存在，且有新增怀疑度公式，将新结果拼接后重新存储
        if SS_ALL_t is not None:
            for add_index in SS_ALL:
                SS_ALL_t[add_index] = SS_ALL[add_index]
        else:
            SS_ALL_t = SS_ALL
        Tool_io.checkAndSave(versionPath[1], "data_SS_all", SS_ALL_t)
        print("SS end")
    return SS_ALL_t


def getCoverageRatioFactor(versionPath, covMatrix, inVector,formulaSus_origin,baseline=True):
    print("CR start")
    #若存在CR结果，则直接返回
    formulaSus = formulaSus_origin
    CR_ALL_t = Tool_io.checkAndLoad(versionPath[1], "data_CR_all")
    if CR_ALL_t != None:
        # 原始CR特征维度
        origin_len = len(CR_ALL_t)
        # 怀疑度公式类型是否有增减
        formulaSus_copy = copy.deepcopy(formulaSus_origin)
        formulaSus, CR_ALL_t = Tool_io.add_del_formula(formulaSus_copy, CR_ALL_t)
        # 怀疑度公式与现有CR特征用到的怀疑度公式类型是否有减少
        now_len = len(CR_ALL_t)
        if now_len < origin_len:
            Tool_io.checkDele(versionPath[1], "data_CR_all")
            if len(formulaSus) == 0:
                Tool_io.checkAndSave(versionPath[1], "data_CR_all", CR_ALL_t)
                return CR_ALL_t
        if len(formulaSus) > 0:
            Tool_io.checkDele(versionPath[1], "data_CR_all")
        else:
            # 怀疑度公式与现有CR特征用到的怀疑度公式类型没有增加，原结果不变或删减后可直接返回
            return CR_ALL_t

    CR_ALL = {}
    for algorithm_k, algorithm_v in formulaSus.items():
        CR = {}
        for case_index in trange(len(covMatrix)):
            #if inVector[case_index] == 0:
            S_num = 0
            Sp_num = 0
            for key, value in formulaSus[algorithm_k]:
                #怀疑分数在0.5-1之间的语句数量
                if(value>=0.5 and value<=1):
                    S_num += 1
                    # 计算怀疑分数在0.5-1之间的并且被执行的语句数量
                    if covMatrix[case_index][key] == 1:
                        Sp_num += 1
            #计算CR值
            if S_num == 0:
                CR[case_index] = 0
            else:
                CR[case_index] = Sp_num / S_num
        CR_ALL[algorithm_k] = CR

    # 若原结果存在，且有新增怀疑度公式，将新结果拼接后重新存储
    if CR_ALL_t is not None:
        for add_index in CR_ALL:
            CR_ALL_t[add_index] = CR_ALL[add_index]
    else:
        CR_ALL_t = CR_ALL
    Tool_io.checkAndSave(versionPath[1], "data_CR_all", CR_ALL_t)
    return CR_ALL_t


def getSimilarityFactor(versionPath,covMatrix,inVector,formulaSus_origin,baseline=True):
    print("SF start")
    # 若存在SF结果，则直接返回
    formulaSus = formulaSus_origin
    SF_ALL_t = Tool_io.checkAndLoad(versionPath[1], "data_SF_all")
    if SF_ALL_t != None:
        # 原始SF特征维度
        origin_len = len(SF_ALL_t)
        # 怀疑度公式类型是否有增减
        formulaSus_copy = copy.deepcopy(formulaSus_origin)
        formulaSus, SF_ALL_t = Tool_io.add_del_formula(formulaSus_copy, SF_ALL_t)
        # 怀疑度公式与现有SF特征用到的怀疑度公式类型是否有减少
        now_len = len(SF_ALL_t)
        if now_len < origin_len:
            Tool_io.checkDele(versionPath[1], "data_SF_all")
            if len(formulaSus) == 0:
                Tool_io.checkAndSave(versionPath[1], "data_SF_all", SF_ALL_t)
                return SF_ALL_t
        if len(formulaSus) > 0:
            Tool_io.checkDele(versionPath[1], "data_SF_all")
        else:
            # 怀疑度公式与现有SF特征用到的怀疑度公式类型没有增加，原结果不变或删减后可直接返回
            return SF_ALL_t


    SF_ALL = {}
    for algorithm_k, algorithm_v in formulaSus.items():
        SF = {}
        Ef = []
    #计算失败测试用例的加权向量
        for case_failed in range(len(covMatrix)):
            if inVector[case_failed] == 1:
                fi = copy.deepcopy(covMatrix[case_failed])
                for key, value in formulaSus[algorithm_k]:
                    fi[key] *= value
                Ef.append(fi)
        for case_index in trange(len(covMatrix)):
            #if inVector[case_index] == 0:
            #计算Ep的加权向量
            Ep = copy.deepcopy(covMatrix[case_index])
            for key, value in formulaSus[algorithm_k]:
                Ep[key] *= value
            #Efi和Ep距离初始值为最大值，也就是程序语句数
            distance = len(covMatrix[case_index])
            # 计算Efi和Ep之间的最短距离
            for fail_index in range(len(Ef)):
                sum = 0
                for index in range(len(Ef[fail_index])):
                    sum = sum+(Ef[fail_index][index]-Ep[index])**2
                if sum**0.5 < distance:
                    distance = sum**0.5
            #计算SF值
            if distance == 0:
                SF[case_index] = 0
            else:
                SF[case_index] = 1 / distance
        SF_ALL[algorithm_k] = SF

    # 若原结果存在，且有新增怀疑度公式，将新结果拼接后重新存储
    if SF_ALL_t is not None:
        for add_index in SF_ALL:
            SF_ALL_t[add_index] = SF_ALL[add_index]
    else:
        SF_ALL_t = SF_ALL
    Tool_io.checkAndSave(versionPath[1], "data_SF_all", SF_ALL_t)
    return SF_ALL_t


def getFaultMaskingFactor(versionPath,covMatrix,inVector,notSort_origin,target,baseline=True):
    print("FM start")
    # 若存在SF结果，则直接返回
    notSort = notSort_origin
    FM_ALL_t = Tool_io.checkAndLoad(versionPath[1], "data_FM_all")
    if FM_ALL_t != None:
        # 原始SF特征维度
        origin_len = len(FM_ALL_t)
        # 怀疑度公式类型是否有增减
        notSort_copy = copy.deepcopy(notSort_origin)
        notSort, FM_ALL_t = Tool_io.add_del_formula(notSort_copy, FM_ALL_t)
        # 怀疑度公式与现有SF特征用到的怀疑度公式类型是否有减少
        now_len = len(FM_ALL_t)
        if now_len < origin_len:
            Tool_io.checkDele(versionPath[1], "data_FM_all")
            if len(notSort) == 0:
                Tool_io.checkAndSave(versionPath[1], "data_FM_all", FM_ALL_t)
                return FM_ALL_t
        if len(notSort) > 0:
            Tool_io.checkDele(versionPath[1], "data_FM_all")
        else:
            # 怀疑度公式与现有FM特征用到的怀疑度公式类型没有增加，原结果不变或删减后可直接返回
            return FM_ALL_t

    #impact factor
    operators={
        '>':0.79,
        '<':0.79,
        '=':0.79,
        '>=':0.79,
        '<=':0.79,
        '+':0.08,
        '-':0.08,
        '*':0.08,
        '/':0.08,
        '%':0.08,
    }
    FM_ALL = {}
    for algorithm_k, algorithm_v in notSort.items():
        FM = {}
        for case_index in trange(len(covMatrix)):
            #if inVector[case_index] == 0:
            for stat_index in range(len(covMatrix[case_index])):
                if covMatrix[case_index][stat_index] == 1:
                    #查找怀疑度大于0.5的第一条被执行过的语句
                    if(algorithm_v[stat_index])>0.5:
                        #查找怀疑度大于0.5的第一条被执行过的语句 的下一条语句
                        list_index = stat_index+1
                        #遍历之后的语句
                        sum_op = 0
                        while list_index < len(covMatrix[case_index]):
                            if covMatrix[case_index][list_index] == 1:
                                text = linecache.getline(target,list_index+1)
                                #取 operators 最大值
                                impact_factor  = 0
                                for k,v in operators.items():
                                 if text.find(k):
                                    if v > impact_factor:
                                        impact_factor = v
                                #语句impact_factor求和
                                sum_op += impact_factor
                            list_index += 1
                        FM[case_index] = sum_op
                        break
                    else:
                        FM[case_index] = 0
                else:
                    FM[case_index] = 0
            FM_ALL[algorithm_k] = FM
    # 若原结果存在，且有新增怀疑度公式，将新结果拼接后重新存储
    if FM_ALL_t is not None:
        for add_index in FM_ALL:
            FM_ALL_t[add_index] = FM_ALL[add_index]
    else:
        FM_ALL_t = FM_ALL
    Tool_io.checkAndSave(versionPath[1], "data_FM_all", FM_ALL_t)
    return FM_ALL_t


def getStatementFactor(versionPath,covMatrix,inVector,notSort,target,baseline=True):
    print("Statement start")
    # 若存在结果，则直接返回
    if baseline:
        ST_ALL = Tool_io.checkAndLoad(versionPath[1], "data_statement_all")
        if ST_ALL != None:
            return ST_ALL
    ST_ALL = {}
    for case_index in trange(len(covMatrix)):
        #if inVector[case_index] == 0:
        num_operators = 0
        num_operands = 0
        for stat_index in range(len(covMatrix[case_index])):
            if covMatrix[case_index][stat_index] == 1:
                text = linecache.getline(target, stat_index+1)
                op, op_key = all_operators()
                operators = op_key
                operands = {}
                if (not text.startswith("//")):
                    text_tmp = ' ' + text.split('//')[0]
                    for key in operators.keys():
                        if key not in op:
                            count = text_tmp.count(' ' + key + ' ')
                            operators[key] = operators[key] + count
                            if count > 0:
                                text_tmp = text_tmp.replace(' ' + key + ' ', ' ')
                        else:
                            operators[key] = operators[key] + text_tmp.count(key)
                            text_tmp = text_tmp.replace(key, ' ')
                    for key in text_tmp.split():
                        if key in operands:
                            operands[key] = operands[key] + 1
                        else:
                            if key != '':
                                operands[key] = 1
                for k, v in operators.items():
                    num_operators += v
                # 计算操作数数量和操作数种类数量
                for m, n in operands.items():
                    num_operands += n
        tmp = {}
        tmp['num_operators'] = num_operators
        tmp['num_operands'] = num_operands
        tmp['loc_len'] = sys.getsizeof(text)
        ST_ALL[case_index] = tmp
    Tool_io.checkAndSave(versionPath[1], "data_statement_all", ST_ALL)
    return ST_ALL


# 计算静态特征
# def getStaticFeature(versionPath,covMatrix,inVector,ochiai,target,baseline=True):
#     # 若存在结果，则直接返回
#     if baseline:
#         STATIC = Tool_io.checkAndLoad(versionPath, "data_STATIC_baseline")
#         if STATIC != None:
#             return STATIC
#     STATIC = {}
#
#     with open(target,'r',encoding='utf-8') as f:
#         res = f.read()
#         res = res.replace('[','').replace(']','')
#         con = res.split(',')
#
#     for case_index in trange(len(covMatrix)):
#         if inVector[case_index] == 0:
#             S_num = 0
#             Sp_num = 0
#             SFPL = 0
#             for key, value in formulaSus["ochiai"]:
#                 #怀疑分数在0.5-1之间的语句数量
#                 if(value>=0.5 and value<=1):
#                     S_num += 1
#                     # 计算怀疑分数在0.5-1之间的并且被执行的语句数量
#                     if covMatrix[case_index][key] == 1:
#                         SFPL += float(con[key])
#             #计算CR值
#             STATIC[case_index] = SFPL / S_num
#     Tool_io.checkAndSave(versionPath, "data_STATIC_baseline", STATIC)
#     return STATIC


# 执行程序
def execution(param):
    versionPath = param[0]
    error_pro_ver = param[1]
    # 获得覆盖信息，测试用例结果
    covMatrix, fault, inVector, failN, passN, realCC, failIndex, trueCC = Tool_io.readFile(versionPath, error_pro_ver)
    # 若结果为空
    if covMatrix == None:
        return None
    # 判断cc是否数量为0
    if len(realCC) == 0:
        f_error = open(os.path.join(error_pro_ver, 'error_loc.txt'), 'a+')
        f_error.writelines(versionPath[0] + " 该版本无cc\r\n")
        f_error.close()
    statement_num = len(covMatrix[0])
    case_num = len(covMatrix)
    # 计算怀疑度分数
    sus_score = Tool_localization.statement_sus(case_num, statement_num, covMatrix, inVector, versionPath)
    # 计算SS
    print(versionPath)
    SS = getSuspiciousnessScoreFactorSimple(versionPath, covMatrix, inVector, sus_score[0])
    # 计算CR
    print(versionPath)
    CR = getCoverageRatioFactor(versionPath, covMatrix, inVector, sus_score[0])
    # 计算SF
    print(versionPath)
    SF = getSimilarityFactor(versionPath, covMatrix, inVector, sus_score[0])
    # 计算FM
    print(versionPath)
    target = os.path.join(versionPath[1], "hugeCodeCopy.txt")
    FM = getFaultMaskingFactor(versionPath, covMatrix, inVector, sus_score[1], target)
    # 归一化特征
    res_nor = Tool_localization.normalization(SS, CR, SF, FM, versionPath)
    return "success"

# baseline方法
def execution_baseline(param):
    versionPath = param[0]
    error_pro_ver = param[1]
    # 获得覆盖信息，测试用例结果
    covMatrix, fault, inVector, failN, passN, realCC, failIndex, trueCC = Tool_io.readFile(versionPath, error_pro_ver)
    # 若结果为空
    if covMatrix == None:
        return None
    # 判断cc是否数量为0
    if len(realCC) == 0:
        f_error = open(os.path.join(error_pro_ver, 'error_loc.txt'), 'a+')
        f_error.writelines(versionPath[0] + " 该版本无cc\r\n")
        f_error.close()
    statement_num = len(covMatrix[0])
    case_num = len(covMatrix)
    sus_score = Tool_localization.statement_sus(case_num, statement_num, covMatrix, inVector, versionPath)

    #模糊加权距离
    FDistance = getSuspiciousnessFDistance(versionPath, covMatrix, inVector, sus_score[0])
    WPcc = FuzzyKnn.fuzzy_knn(FDistance, failIndex, trueCC, versionPath)
    res = FuzzyKnn.fuzzy_knn_metric(realCC, WPcc,versionPath,error_pro_ver)

    return res

if __name__ =="__main__":

    #windows path
    # root = 'D:\\CC\\data_test\\data'
    # data = 'D:\\CC\\data_test\\other'
    # error_pro_ver = 'D:\\CC\\data_test\\error'
    # res_path = 'D:\\CC\\data_test\\res'

    # linux path sss
    root = '/home/tianshuaihua/dataset'
    data = '/home/tianshuaihua/pydata'
    error_pro_ver = '/home/tianshuaihua/error'
    res_path = '/home/tianshuaihua/res'

    # baseliness
    # root = '/home/tianshuaihua/base_dataset'
    # data = '/home/tianshuaihua/base_pydata'
    # error_pro_ver = '/home/tianshuaihua/base_error'
    # res_path = '/home/tianshuaihua/base_res'

    # 获取程序路径
    res = Tool_io.create_data_folder(root,data)
    for index in res:
        print(index)
        pool = Pool(processes=4)
        for ver in res[index]:
            pro_name = os.path.basename(index)
            param = []
            param.append(ver)
            param.append(error_pro_ver)
            # if pro_name == 'Math':
            #print(os.path.basename(ver[0]))
            pool.apply_async(execution, (param,))
            # else:
            #     continue
        pool.close()
        pool.join()
        print("current program end")
    #machine_learning(root,data,error_pro_ver,res_path)

    # execution(ver[index], error_pro_ver)ss
    # for i in range(len(all_files)):sss
    #     p.apply(func=execution, args=(all_files[i],))  # 异步ss
    # p.close()
    # p.join()  # 异步调用apply_async,需要添加这一行

    # for index in range(len(all_files)):
    #     print(index)
    #     if index!=2 and index != 7:
    #         execution(all_files[index],error_pro_ver)

    #chart 3b不可用
    # for index in range(26):
    #     if 0 <= index < 26 and index != 2:
    #         execution(all_files[index],error_pro_ver)

    # execution_baseline(all_files[11]) s



    # 回归静态特征
    #target = os.path.join(versionPath, "hugeCodeCopy.txt")
    #STATMENT = getStatementFactor(versionPath, covMatrix, inVector, notSort, target)


    # 计算STATAIC
    #targetStatic = os.path.join(versionPath, "static_fea_copy.txt")
    #STATIC_FEA = getStaticFeature(versionPath, covMatrix, inVector, ochiai, targetStatic)


    # for k,v in SF.items():
    #    if v>1:
    #        print((k,v))

    # print(time.time())
    # matlab_fun = fuzzyCal.initialize()
    # cal = matlab_fun.fuzzyCal(float(0.0), float(0.0), float(0.618522873486732), float(0.0), float(0.0))
    # print(cal)


    # result = []
    # matlab_fun = fuzzyCal.initialize()
    # for index in trange(len(SS)):
    #     if SS.__contains__(index):
    #         one = float(SS[index])
    #         two = float(CR[index])
    #         three = float(SF[index])
    #         four = float(FM[index])
    #         five = float(STATIC_FEA[index])
    #         cal = matlab_fun.fuzzyCal(one,two,three,four,five)
    #         result.append(cal)
    #
    # with open('D:\\CC\\data_test\\result.txt','a',encoding='utf-8') as f:
    #     for i in result:
    #         f.write(str(i)+'\n')


    #engine = matlab.engine.start_matlab()
    #result=engine.Cal(2,3)
    #result = engine.fuzzyCal(0.6,0.4,0.7,0.8,0.5)
    #print(result)




    # print(time.time())
    # matlab_fun = fuzzyCal.initialize()
    # cal = matlab_fun.fuzzyCal(0.4, 0.6, 0.7, 0.8, 0.6)
    # print(cal)


