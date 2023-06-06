import pandas as pd
import zlib
from io import StringIO

# 解压数据集 类型为dataframe
def zlibdecompress_dataframe(data):
    result2 =  zlib.decompress(data).decode('utf8')
    data = pd.read_csv(StringIO(result2), skipinitialspace=True)
    return data

def zlibcompress(data):
    if type(data) == pd.Series:
        data = data.to_frame()
    if type(data)==dict:
        data = bytes('{}'.format(data),'utf8')
    if type(data) == str:
        data = bytes(data,'utf8')
    if type(data)==pd.DataFrame:
        data = bytes(data.to_csv(line_terminator='\r\n',index=False),encoding='utf8')
    if type(data) == tuple:
        data = bytes('{}'.format(data),'utf8')
    s_out = zlib.compress(data)
    return s_out
