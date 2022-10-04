# coding=utf-8

import math
import os

# 使用时打开注释
#import javalang
#import lizard
import linecache
import pickle
import Static_code_machine
import pandas as pd
import numpy as np
import Sttaic_code_features


# lizard计算程序静态特征 按函数划分
from DealComplexity import getDeclareList, get_folder, getAllJavaFile


def cal_code(file_path):
    # 使用时打开注释
    #res = lizard.analyze_file(file_path)
    return res.function_list


# 统计Halstead 操作数和操作符数量
def halstead_cal(codes):
    Ioc_blank = 0
    op, op_key = all_operators()
    operators = op_key
    operands = {}
    isAllowed = True
    for text in codes:
        # 统计空白行
        if text == '':
            Ioc_blank += 1
        else:
            # 统计操作符和操作数的数量
            if text.startswith("/*"):
                isAllowed = False
            if (not text.startswith("//")) and isAllowed == True:
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

            if text.endswith("*/"):
                isAllowed = True
        # 计算操作符数量和操作符种类数量
        operators.pop(')')
        operators.pop(']')
        operators.pop('}')
        num_operators = 0
        num_unique_operators = 0
        for k, v in operators.items():
            num_operators += v
            if v != 0:
                num_unique_operators += 1
        # 计算操作数数量和操作数种类数量
        num_operands = 0
        num_unique_operands = 0
        for m, n in operands.items():
            num_operands += n
            if n != 0:
                num_unique_operands += 1
        h = halstead_fun(num_operators, num_operands, num_unique_operators, num_unique_operands)
        return h, Ioc_blank


# java 操作数&操作符
def all_operators():
    op = {'(': 0, ')': 0, '{': 0, '}': 0, '[': 0, ']': 0, ',': 0, '.': 0, ':': 0, '>': 0, '<': 0, '!': 0,
          '~': 0, '?': 0, '::': 0, '<:': 0, '>:': 0, '!:': 0, '&&': 0, '||': 0, '++': 0, '--': 0, '+': 0,
          '-': 0, '*': 0, '/': 0, '&': 0, '|': 0, '^': 0, '%': 0, '->': 0, '::': 0, '+:': 0, '-:': 0, '*:': 0, '/:': 0,
          '&:': 0, '|:': 0, '^:': 0, '%:': 0, '<<:': 0, '>>:': 0, '>>>:': 0, '@': 0, '...': 0, '==': 0, '=': 0}

    op_key = {'(': 0, ')': 0, '{': 0, '}': 0, '[': 0, ']': 0, ';': 0, ',': 0, '.': 0, ':': 0, '>': 0, '<': 0, '!': 0,
              '~': 0, '?': 0, '::': 0, '<:': 0, '>:': 0, '!:': 0, '&&': 0, '||': 0, '++': 0, '--': 0, '+': 0,
              '-': 0, '*': 0, '/': 0, '&': 0, '|': 0, '^': 0, '%': 0, '->': 0, '::': 0, '+:': 0, '-:': 0, '*:': 0,
              '/:': 0, '&:': 0, '|:': 0, '^:': 0, '%:': 0, '<<:': 0, '>>:': 0, '>>>:': 0, '@': 0, '...': 0, '==': 0,
              '=': 0, 'abstract': 0, 'assert': 0, 'boolean': 0, 'break': 0, 'byte': 0, 'case': 0, 'catch': 0, 'char': 0,
              'class': 0, 'const': 0, 'continue': 0, 'default': 0, 'do': 0, 'double': 0, 'else': 0, 'enum': 0,
              'extends': 0, 'final': 0, 'finally': 0, 'float': 0, 'for': 0, 'if': 0, 'goto': 0, 'implements': 0,
              'import': 0, 'instanceof': 0, 'int': 0, 'interface': 0, 'long': 0, 'native': 0, 'new': 0, 'package': 0,
              'private': 0, 'protected': 0, 'public': 0, 'return': 0, 'short': 0, 'static': 0, 'strictfp': 0,
              'super': 0, 'switch': 0, 'synchronized': 0, 'this': 0, 'throw': 0, 'throws': 0, 'transient': 0,
              'try': 0, 'void': 0, 'volatile': 0, 'while': 0, 'null': 0, 'Integer': 0, 'Long': 0,
              'String': 0, 'Double': 0, 'Float': 0}

    return op, op_key


# 计算Halstead复杂度
def halstead_fun(n1, n2, u1, u2):
    N = n1 + n2
    U = u1 + u2
    V = N * math.log(U, 2)
    D = (u1 * n2) / (2 * u2)
    E = D * V
    T = E / 18
    B = (E ** (2 / 3)) / 3000
    L = 1 / D
    h = {'h_N': N, 'h_V': V, 'h_D': D, 'h_E': E, 'h_B': B, 'h_T': T, 'h_L': L}
    return h


# 遍历项目所有java文件
def java_files(files):
    code_all_feature = []
    for file_path in files:
        tmp = str(file_path).split('\\fun_change_name\\')
        pkg = tmp[1].split('\\')
        if len(pkg) == 1:
            pkg_name = pkg[0].split('.')[0]
        else:
            pkg_name = '.'.join(pkg)[:-5]
        code_file_feature = cal_file_complexity(file_path, pkg_name)
        code_all_feature = code_all_feature + code_file_feature
    return code_all_feature


ClassDeclareList = {}

# 统计类
def analysisList(tree):
    global ClassDeclareList
    global FunctionDeclareList
    if type(tree) == list:
        for item in tree:
            if item != None:
                analysisList(item)
    else:
        if ("InterfaceDeclaration" in str(type(tree)) or "ClassDeclaration" in str(type(tree))):
            ClassName = tree.name
            ClassDeclareList[ClassName] = tree
        if hasattr(tree, 'body'):
            childList = tree.body
            if "BlockStatement" not in str(type(childList)):
                analysisList(childList)
            else:
                childList = childList.children
                analysisList(childList)


# 统计函数变量数量
def calVariable():
    global ClassDeclareList
    file_var = {}
    for k, v in ClassDeclareList.items():
        class_var = {}
        for method in v.body:
            if 'FieldDeclaration' in str(type(method)):
                class_var['var'] = len(method.declarators)
            if "ConstructorDeclaration" in str(type(method)) or 'MethodDeclaration' in str(type(method)):
                var_count = 0
                if method.body != None:
                    for variable in method.body:
                        if 'LocalVariableDeclaration' in str(type(variable)):
                            var_count = var_count + 1
                class_var[method.name] = var_count
        if not class_var.__contains__('var'):
            class_var['var'] = 0
        file_var[k] = class_var
    # 统计文件内全部 全局变量和局部变量
    all_var = 0
    all_local_var = 0
    for key,value in file_var.items():
        for k,v in value.items():
            if k == 'var':
                all_var = all_var + v
            else:
                all_local_var = all_local_var + v
    return file_var, all_var, all_local_var


# 计算单文件复杂度
def cal_file_complexity(file_path, pkg_name):
    function_list = cal_code(file_path)
    code_file_feature = []

    # 统计变量
    fd = open(file_path, "r", encoding="utf-8")  # 读取Java源代码
    var_lines = fd.readlines()
    var_content = ''.join(var_lines)
    #使用时打开注释
    #tree = javalang.parse.parse(var_content)  # 根据源代码解析出一颗抽象语法树
    tree = 2
    analysisList(tree.children)
    #print(file_path)
    file_var, all_var, all_local_var = calVariable()

    for function_index in function_list:
        code_info = {}
        tmp = function_index.__dict__
        codes = []
        for statement_index in range(tmp['start_line'], tmp['end_line'] + 1):
            text = linecache.getline(file_path, statement_index).strip()
            codes.append(text)
        h, Ioc_blank = halstead_cal(codes)
        code_info['parameters'] = len(tmp['full_parameters'])
        code_info['functions'] = len(function_list)
        code_info['token_count'] = tmp['token_count']
        code_info['top_nesting_level'] = tmp['top_nesting_level']
        code_info['h_N'] = h['h_N']
        code_info['h_N'] = h['h_N']
        code_info['h_V'] = h['h_V']
        code_info['h_D'] = h['h_D']
        code_info['h_E'] = h['h_E']
        code_info['h_B'] = h['h_B']
        code_info['h_T'] = h['h_T']
        code_info['h_L'] = h['h_L']
        code_info['number_of_lines'] = tmp['end_line'] - tmp['start_line'] + 1
        code_info['loc_executable'] = tmp['nloc']
        code_info['loc_blank'] = Ioc_blank
        code_info['loc_comments'] = tmp['end_line'] - tmp['start_line'] + 1 - tmp['nloc'] - Ioc_blank
        code_info['loc_code_and_comment'] = tmp['end_line'] - tmp['start_line'] + 1 - Ioc_blank
        code_info['cyclomatic_complexity'] = tmp['cyclomatic_complexity']
        # 统计变量数量
        na_len = len(str(tmp['name']).split('::'))
        na = str(tmp['name']).split('::')[na_len-1]
        for k, v in file_var.items():
            for m,n in v.items():
                if m == na:
                    code_info['local_var'] = n
        code_info['all_var'] = all_var
        code_info['all_local_var'] = all_local_var
        # 测试用例结果
        err_loc = str(file_path).split("\\source\\")[0] + '\\faultLineSimpleIndex.txt'
        f = open(err_loc, 'rb')
        error_con = pickle.load(f)

        error_key = '/' + ('source.' + pkg_name).replace('.', '/') + '.java'
        if error_con.__contains__(error_key):
            if tmp['start_line'] <= error_con[error_key][0] <= tmp['end_line']:
                code_info['error_flag'] = 1
            else:
                code_info['error_flag'] = 0
        else:
            code_info['error_flag'] = 0
        # 拼接函数名称
        names = pkg_name.split('.')
        name_len = len(pkg_name.split('.'))
        py_names = str(tmp['name']).split('::')
        last_name = ''
        for index in range(len(py_names)):
            if index == 0:
                continue
            else:
                last_name = last_name + '.' + py_names[index]
        if names[name_len - 1] == str(tmp['name']).split('::')[0]:
            code_info['name'] = pkg_name + last_name
        else:
            names[name_len - 1] = str(tmp['name']).split('::')[0]
            pkg_name = '.'.join(names)
            code_info['name'] = pkg_name + last_name
        if code_info['name'] != 'org.jfree.chart.axis.SegmentedTimeline.while':
            code_file_feature.append(code_info)
    return code_file_feature


# 汇总全部静态代码特征(弃用)
def complexity_all(file_path, comp_path):
    complexity = comp(comp_path)
    function_list = cal_code(file_path)
    code_static_feature = []
    for function_index in function_list:
        tmp = function_index.__dict__
        code_info = {}
        Ioc_blank = 0
        op, op_key = all_operators()
        operators = op_key
        operands = {}
        isAllowed = True
        for statement_index in range(tmp['start_line'], tmp['end_line'] + 1):
            text = linecache.getline(file_path, statement_index).strip()
            if text == '':
                Ioc_blank += 1
            else:
                # 统计操作符和操作数的数量
                if text.startswith("/*"):
                    isAllowed = False
                if (not text.startswith("//")) and isAllowed == True:
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

                if text.endswith("*/"):
                    isAllowed = True

        # 计算操作符数量和操作符种类数量
        operators.pop(')')
        operators.pop(']')
        operators.pop('}')
        num_operators = 0
        num_unique_operators = 0
        for k, v in operators.items():
            num_operators += v
            if v != 0:
                num_unique_operators += 1
        # 计算操作数数量和操作数种类数量
        num_operands = 0
        num_unique_operands = 0
        for m, n in operands.items():
            num_operands += n
            if n != 0:
                num_unique_operands += 1

        h = halstead_fun(num_operators, num_operands, num_unique_operators, num_unique_operands)
        code_info['h_N'] = h['h_N']
        code_info['h_V'] = h['h_V']
        code_info['h_D'] = h['h_D']
        code_info['h_E'] = h['h_E']
        code_info['h_B'] = h['h_B']
        code_info['h_T'] = h['h_T']
        code_info['h_L'] = h['h_L']
        code_info['number_of_lines'] = tmp['end_line'] - tmp['start_line'] + 1
        code_info['loc_executable'] = tmp['nloc']
        code_info['loc_blank'] = Ioc_blank
        code_info['loc_comments'] = tmp['end_line'] - tmp['start_line'] + 1 - tmp['nloc'] - Ioc_blank
        code_info['loc_code_and_comment'] = tmp['end_line'] - tmp['start_line'] + 1 - Ioc_blank
        code_info['cyclomatic_complexity'] = tmp['cyclomatic_complexity']
        # 整合其他复杂度信息(essential complexity, design complexity)
        fun_name = str(tmp['name'])
        r = len(fun_name.split('::'))
        if r > 2:
            print(fun_name)
        continue
        if fun_name.find('CycleBoundTick::CycleBoundTick') > 0:
            print(fun_name)
        fun_name = fun_name.replace('::', '.')
        fun_name += '('
        seven = 0
        for parameter in tmp['full_parameters']:
            par = str(parameter).strip()
            array = par.split(' ')
            flag = 0
            if array[len(array) - 1] == ']':
                array.pop()
                array.pop()
            if len(array) > 2:
                par = (array[0] + array[1] + array[2]).replace(' ', '')
            else:
                par = array[0].replace(' ', '')
            fun_name += par + ','
            seven = seven + 1
            if seven == 7:
                break;
        fun_name = fun_name.strip(',') + ')'

        code_info['function_name'] = fun_name
        comp_info = complexity[fun_name]
        code_info['essential_complexity'] = comp_info.split('-')[0]
        code_info['design_complexity'] = comp_info.split('-')[1]
        code_static_feature.append(code_info)
    return code_static_feature


# 处理特征数据(整理成二维数组形式)
def deal_features_data(data):
    features_arr = []
    fun_name = []
    fun_res = []
    for features in data:
        arr = []
        fun_name.append(features['name'])
        fun_res.append(features['error_flag'])
        for k, v in features.items():
            if k != 'name' and k != 'error_flag':
                arr.append(v)
        features_arr.append(arr)
    return features_arr, fun_name, fun_res


# 递归遍历文件夹
def show_files(base_path, all_files=[]):
    file_list = os.listdir(base_path)
    # 准备循环判断每个元素是否是文件夹还是文件，是文件的话，把名称传入list，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        cur_path = os.path.join(base_path, file)
        # 判断是否是文件夹
        if os.path.isdir(cur_path):
            show_files(cur_path, all_files)
        else:
            if not file.endswith('.java'):
                continue
            else:
                all_files.append(cur_path)
    return all_files


# 读取复杂度文件
def comp(comp_path):
    file_comp = open(comp_path, 'r', encoding='utf-8')
    list_stat = file_comp.readlines()
    complexity = {}
    name = []
    for index_row in range(len(list_stat)):
        row = str(list_stat[index_row]).strip().split('-')
        name.append(row[0])
        complexity[row[0]] = row[2] + '-' + row[3]
        # if complexity.__contains__(row[0]):
        #     res = complexity[row[0]]
        #     res = res + 1
        #     complexity[row[0]] = res
        # else:
        #     complexity[row[0]] = 0
    return complexity, name


# 生成静态特征向量
def static_code(all_path,dir,fea):
    path = all_path + '\\' + dir + '\\source\\fun_change_name'
    files = getAllJavaFile(path)
    matrix = []
    for file in files:
        java_f = path+file
        with open(java_f,'r',encoding='utf-8') as f:
            lines = f.readlines()
            matrix_tmp = [-1] * len(lines)
            fun_list = cal_code(java_f)
            for fun_index in fun_list:
                tmp = fun_index.__dict__
                start = tmp['start_line'] - 1
                end = tmp['end_line']

                names = java_f[:-5].split('\\')
                name_len = len(java_f[:-5].split('\\'))
                py_names = str(tmp['name']).split('::')
                last_name = ''
                true_name = ''
                for index in range(len(py_names)):
                    if index == 0:
                        continue
                    else:
                        last_name = last_name + '.' + py_names[index]
                if names[name_len - 1] == str(tmp['name']).split('::')[0]:
                    true_name = java_f[:-5] + last_name
                else:
                    names[name_len - 1] = str(tmp['name']).split('::')[0]
                    true_name = '\\'.join(names) + last_name

                key_name = true_name.split('fun_change_name\\')[1].replace('\\','.')
                #if key_name == ''
                if key_name != 'org.jfree.chart.axis.SegmentedTimeline.while':

                    matrix_tmp[start:end] = (end - start) * [fea[key_name]]
        matrix = matrix+matrix_tmp
    if os.path.exists(all_path + '\\' + dir+'\\static_fea.txt'):
        print('exist: '+all_path + '\\' + dir+'\\static_fea.txt')
    else:
        static_file = open(all_path + '\\' + dir+'\\static_fea.txt', 'w', encoding='utf-8')
        static_file.write(str(matrix))
        static_file.close()


if __name__ == '__main__':


    files = show_files('D:\\CC\\data_test\\Chart\\1b\\source\\fun_change_name')
    files_feature = java_files(files)

    # for index in files_feature:
    #     if not index.__contains__('local_var'):
    #         print(index)

    complexity, name = comp('D:\\CC\\data_test\\Chart\\1b\\complexity.txt')

    for features in files_feature:
        name = features['name']
        if not name.find("fun"):
            print(name)
        if complexity.__contains__(name):
            features['essential_complexity'] = int(str(complexity[name]).split('-')[0])
            features['design_complexity'] = int(str(complexity[name]).split('-')[1])

    # tt = {}
    # for er in files1:
    #     key = er['name']
    #     tt[key] = 1
    #     if key == 'org.jfree.chart.axis.SegmentedTimeline.while':
    #         print("ex")
    # # print(complexity['org.jfree.data.xy.YWithXInterval.equals'])
    # for k,v in tt.items():
    #     if complexity.__contains__(k):
    #         complexity.pop(k)
    #     else:
    #         print(k)
    # print("s")

    # f = open("D:\\CC\\data_test\\error\\Chart\\1b\\faultLineSimpleContent.txt", 'rb')
    # line = pickle.load(f)
    # print("s")
    # for sss in files_feature:
    #     if sss['error_flag'] == 1:
    #         print(sss)

    features_arr, fun_name, fun_res = deal_features_data(files_feature)
    array = np.array(features_arr)
    pca_data = Static_code_machine.pca_sklearn(array)
    res = Static_code_machine.ridge_sklearn(pca_data, fun_res)


    fea_dict = {}
    ss ={}
    for index in range(len(fun_name)):
        fea_dict[fun_name[index]] = res[index]
        # arr = fun_name[index].split('.')
        # arr_len = len(arr)
        # if ss.__contains__(arr[arr_len-1]):
        #     tmp = ss[arr[arr_len-1]]
        #     tmp = tmp + 1
        #     ss[arr[arr_len - 1]] = tmp
        # else:
        #     ss[arr[arr_len - 1]] = 0
        # if ss[arr[arr_len - 1]]>0:
        #     print(fun_name[index])

    dirs, folder = get_folder('D:\\CC\\data_test\\Chart')
    for dir in dirs:
        static_code('D:\\CC\\data_test\\Chart',dir,fea_dict)

    print(fea_dict)
    # np.array()


