# !/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import getopt
import shutil
import time
from distutils.core import setup
from Cython.Build import cythonize
from Cython.Compiler import Options
from multiprocessing import cpu_count, Pool
from functools import partial
import multiprocessing
from joblib import Parallel, delayed

# currdir = os.path.abspath('.') + '/'
# print('currdir-----',currdir)

# 是否删除.c编译文件, 默认True
delC = True
# 是否删除.o编译文件, 默认True
delO = True
# 是否删除.py源代码文件, 默认False, 参数可由外部参数指定
delPy = False

# v1.4.3 编译py清单

block=[
    'python/fate_flow/web_server/blocks/components/component.py',
    'python/fate_flow/web_server/blocks/components/param.py'
    ,'python/fate_flow/web_server/blocks/components/stream.py'

    ,'python/fate_flow/web_server/blocks/models/kmeans.py'
    ,'python/fate_flow/web_server/blocks/models/lightgbm.py'
       ,'python/fate_flow/web_server/blocks/models/linear_regression.py'
    ,'python/fate_flow/web_server/blocks/models/logistic_regression.py'
    ,'python/fate_flow/web_server/blocks/models/model_base.py'
    ,'python/fate_flow/web_server/blocks/models/neural_network.py'
    ,'python/fate_flow/web_server/blocks/models/secure_boost.py'
    ,'python/fate_flow/web_server/blocks/models/xgboost.py'
    ,'python/fate_flow/web_server/blocks/test/test_blocks.py'
    ,'python/fate_flow/web_server/blocks/application.py'


    # ,'python/fate_flow/web_server/blocks/dummy.py'
    # ,'python/fate_flow/web_server/blocks/group.py'
    # ,'python/fate_flow/web_server/blocks/job_config.py'
    # ,'python/fate_flow/web_server/blocks/templates.py'
    # ,'python/fate_flow/web_server/blocks/utils.py'
    ]
cron = ['python/fate_flow/web_server/crons/detector.py']
db=['python/fate_flow/web_server/db/db_models.py']
db_service=['python/fate_flow/web_server/db_service/common_service.py'
    ,'python/fate_flow/web_server/db_service/model_service.py'
    ,'python/fate_flow/web_server/db_service/party_service.py'
    ,'python/fate_flow/web_server/db_service/project_service.py',
            'python/fate_flow/web_server/db_service/user_service.py']
fl_apps=['python/fate_flow/web_server/fl_apps/approve_app.py',
         'python/fate_flow/web_server/fl_apps/external_app.py',
         'python/fate_flow/web_server/fl_apps/log_manage_app.py',
         'python/fate_flow/web_server/fl_apps/model_manage_app.py',
         'python/fate_flow/web_server/fl_apps/model_train_app.py',
         'python/fate_flow/web_server/fl_apps/node_app.py',
         'python/fate_flow/web_server/fl_apps/own_app.py',
         'python/fate_flow/web_server/fl_apps/project_app.py'
    ,'python/fate_flow/web_server/fl_apps/sample_app.py',
         'python/fate_flow/web_server/fl_apps/socket_app.py',
         'python/fate_flow/web_server/fl_apps/user_app.py']
report=['python/fate_flow/web_server/report/fl_report_data/clustering.py',
        'python/fate_flow/web_server/report/fl_report_data/cv_curves.py',
        'python/fate_flow/web_server/report/fl_report_data/cv_metrics.py',
        'python/fate_flow/web_server/report/fl_report_data/dataset.py',
        'python/fate_flow/web_server/report/fl_report_data/feature_importance.py',
        'python/fate_flow/web_server/report/fl_report_data/linear_weight.py',
        'python/fate_flow/web_server/report/fl_report_data/matrix.py',
        'python/fate_flow/web_server/report/fl_report_data/psi.py',
        'python/fate_flow/web_server/report/fl_report_data/trees.py',
        'python/fate_flow/web_server/report/graph/psi.py',
        'python/fate_flow/web_server/report/metric/cv_metrics.py',
        'python/fate_flow/web_server/report/metric/metrics.py',
        'python/fate_flow/web_server/report/model/clustering.py',
        'python/fate_flow/web_server/report/model/feature_importance.py',
        'python/fate_flow/web_server/report/model/linear_weight.py',
        'python/fate_flow/web_server/report/model/scorecard.py',
        'python/fate_flow/web_server/report/model/trees.py',
        'python/fate_flow/web_server/report/api.py',
        'python/fate_flow/web_server/report/component.py',
        'python/fate_flow/web_server/report/content.py',
        'python/fate_flow/web_server/report/dummy.py',
        'python/fate_flow/web_server/report/reporter.py']
utils = ['python/fate_flow/web_server/utils/common_util.py',
         'python/fate_flow/web_server/utils/decorator_util.py',
         'python/fate_flow/web_server/utils//df_apply.py',
         'python/fate_flow/web_server/utils/enums.py',
         'python/fate_flow/web_server/utils/hdfs_util.py',
         'python/fate_flow/web_server/utils/job_utils.py',
         'python/fate_flow/web_server/utils/redis_util.py',
         'python/fate_flow/web_server/utils/socket_util.py',
         'python/fate_flow/web_server/utils/websocket_util.py']
other=['python/fate_flow/web_server/fl_config.py',
       'python/fate_flow/web_server/init_data.py']


sources = dict()

# ok

sources['cron']=cron
sources['db']=db
sources['db_service']=db_service
sources['block']=block

# # flapps can not compile
# sources['fl_apps']=fl_apps

sources['report']=report
sources['utils']=utils
# web socket can not compile
# sources['websocket']=websocket
sources['other']=other


# 命令行帮助指南
def print_help():
    print("""USAGE: shortopts(-) longopts(--)
    -m --module=[module_name]     all(全部编译) or module_name(指定模块): 
    -d --delpy=[true]             true(删除源码) or false(不删除源码)
    P.S. 指定模块: mpc or fl (da/dt/intersect/iv/lightGBM/LR/PCA) (模块名即目录名)
    短命令: python setup.py -m all -d true
    长命令: python setup.py --module=iv --delpy=false
    示例： python setup.py -m mpc -d false""")
    sys.exit(-1)


# 命令行参数模块,获取参数值
def initOptions():
    config = {
        "module": "",
    }
    opts, args = getopt.getopt(sys.argv[1:], 'm:d:h', ['module=', 'delPy=' 'help'])
    if len(opts) < 2:
        print_help()
    for option, value in opts:
        if option in ["-h", "--help"]:
            print_help()
        elif option in ['-m', '--module']:
            config["module"] = value
        elif option in ['-d', '--delPy']:
            config["delPy"] = value
        if value is None or value == "":
            print("option value is null:" + option)
            sys.exit(-1)
    return config


def getpy(basepath, module):
    fullpath = os.path.join(basepath, module)
    for fname in os.listdir(fullpath):
        if fname not in exclude_so:
            ffile = os.path.join(fullpath, fname)
            if os.path.isdir(ffile):
                for f in getpy(os.path.join(fullpath, fname), ffile):
                    yield f
            elif os.path.isfile(ffile) and os.path.splitext(fname)[1] in ['.py']:
                yield os.path.join(fullpath, fname)


# 指定命令行参数格式，并获取参数
args = initOptions()
print('==>> START:编译代码')
module = args["module"]
delPy = True if args["delPy"].lower() == 'true' else False

exclude_so = ['__init__.py', "setup.py"]
build_dir = "build"
build_tmp_dir = build_dir + "/temp"
Options.docstrings = False
compiler_directives = {'optimize.unpack_method_calls': False, 'always_allow_keywords': True}

start_compile_time = int(round(time.time() * 1000))

modules = dict()
if module == 'all':
    modules = sources
else:
    modules[module] = sources.get(module)


def func(modules1):
    for module in modules1:
        algo = modules.get(module)
        start_module_time = int(round(time.time() * 1000))
        try:
            print('-----module {} start compile'.format(module))
            print(algo)
            setup(name='v1.4.3',
                  ext_modules=cythonize(algo, exclude=None, nthreads=20, quiet=True,
                                        language_level=3, compiler_directives=compiler_directives),
                  script_args=['build_ext', '-b', build_dir, '-t', build_tmp_dir, '--inplace'])
        except Exception as ex:
            print(str(ex))
            print('----module {} compile failed'.format(module))
        else:
            print('==>> 模块:{}完成编译'.format(module))
            if delPy:
                print('==>> 删除.py源代码文件')
                for py_path in algo:
                    print(py_path)
                    os.remove(py_path)
            if delC:
                print('==>> 删除.c文件')
                for py_path in algo:
                    c_path = py_path.replace('.py', '.c')
                    print(c_path)
                    os.remove(c_path)
        end_module_time = int(round(time.time() * 1000))
        print('==>> 模块:{}编译耗时:{}(ms)'.format(module, end_module_time - start_module_time))
        print('========================================================================')




import math

cpuPoolSize = multiprocessing.cpu_count()
sliceSize = max(len(list(sources.keys())) // (max(multiprocessing.cpu_count(), 1)), 1)
iternum = max(math.ceil(len(list(sources.keys())) / sliceSize), 1)

lamdfun2P = partial(func)
lld2 = Parallel(n_jobs=cpuPoolSize)(delayed(lamdfun2P)(
    list(sources.keys())[i * sliceSize:(i + 1) * sliceSize]) for i in range(iternum))

if delO:
    print('==>> 删除.o文件根目录:{}'.format(build_dir))
    shutil.rmtree(build_dir)
end_compile_time = int(round(time.time() * 1000))
print('==>> END:编译代码,耗时:{}(ms)'.format(end_compile_time - start_compile_time))
