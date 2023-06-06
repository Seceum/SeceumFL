import random
from math import gcd,ceil,log
from gmssl import sm3


#数据类型转换
#整数到字节的转换，接收非负整数x和字节串的目标长度k，k满足2^2k>x，返回值是长为k的字节串，k是给定的参数
#整体思路是先在左边填充0将x变为k*8位16进制数串，再每2位合成1个字节
def int_to_bytes(x,k):
    if pow(256,k) <= x:
        raise Exception(f"无法实现整数到字节串的转换，目标字节串长度过短！")
    s = hex(x)[2:].rjust(k*2,'0') # s是k*2位十六进制串
    M = b''
    for i in range(k):
        M = M + bytes([eval('0x' + s[i*2:i*2+2])])
    return M

#字节串到整数的转换，接收长度为k的字节串，返回值是整数x
#整体思路是从后往前便利M，每个字节的基数是2^8
def bytes_to_int(M):
    k = len(M) # k是字节串的长度
    x = 0 # x存储最后的整数
    for i in range(k-1,-1,-1):
        x += pow(256,k-1-i) * M[i]
    return x

#比特串到字节串的转换，接受长度为m的比特串s，返回长度为k的字节穿M，其中k=m/8向上取整
#先判断字符串整体是否能正好转换为字节串，即长度是否为8的倍数,若不整除将其左填充0
def bits_to_bytes(s):
    k = ceil(len(s)/8)
    s = s.rjust(k*8,'0')
    M = b''#M存储要返回的字节串
    for i in range(k):
        M = M + bytes([eval('0b' + s[i*8:i*8+8])])
    return M

#字节串到比特串的转换，接受长度为k的字节串M，返回长度为m的比特串s，其中m=8k,字节串逐位处理
#整体思想是把每一个字节变为8位比特串，用列表存储，最后链接起来
def bytes_to_bits(m):
    s_list = []
    for i in m:
        s_list.append(bin(i)[2:].rjust(8,'0'))
    s = ''.join(s_list)
    return s

#域元素到字节串的转换，域元素是整数，转换成字节串要明确长度，文档规定域元素转换为字节串的长度
def fielde_to_bytes(e):
    q = eval('0x'+'8542D69E 4C044F18 E8B92435 BF6FF7DE 45728391 5C45517D 722EDB8B 08F1DFC3'.replace(' ',''))
    t = ceil(log(q,2))
    l = ceil(t/8)
    return int_to_bytes(e,l)

#字节穿到域元素的转换，直接调用bytes_to_int()，接收的参数是字节串M，返回域元素a,域元素不用填充
def bytes_to_fielde(m):
    return bytes_to_int(m)

#域元素到整数的转换,直接返回
def fielde_to_int(a):
    return a

#点到字节串的转换，接收的参数是椭圆曲线上的点p，元组表示，输出字节串S，选用未压缩表示形式
def point_to_bytes(P):
    xp,yp = P[0],P[1]
    x = fielde_to_bytes(xp)
    y = fielde_to_bytes(yp)
    PC = bytes([0x04])
    s = PC + x+ y
    return s

#字节串到点的转换，接受的参数是字节串s，返回椭圆曲线上的点p，点p的坐标用元组表示
def bytes_to_point(s):
    # if len(s) % 2 == 0:
    #     raise Exception(f"无法实现字节串到点的转换，请检查字节串是否为未压缩形式！")
    l = (len(s) - 1) // 2
    PC = s[0]
    x = s[1:l+1]
    y = s[l+1:2*l+1]
    xp = bytes_to_fielde(x)
    yp = bytes_to_fielde(y)
    P = (xp,yp) # 此处缺少检验点p是否在椭圆曲线上
    return P

#域元素到比特串
def fielde_to_bits(a):
    a_bytes = fielde_to_bytes(a)
    a_bits = bytes_to_bits(a_bytes)
    return a_bits

#点到比特串
def point_to_bits(P):
    p_bytes = point_to_bytes(P)
    p_bits = bytes_to_bits(p_bytes)
    return p_bits

#整数到比特串
def int_to_bits(x):
    x_bits = bin(x)[2:]
    k = ceil(len(x_bits)/8)#8位1组，k是组数，目的是方便对齐
    x_bits = x_bits.rjust(k*8,'0')
    return x_bits

#字节串到十六进制串
def bytes_to_hex(m):
    h_list = []#h_list存储十六进制串中的每一部分
    for i in m:
        e = hex(i)[2:].rjust(2,'0')#不能把0掉
        h_list.append(e)
    h = ''.join(h_list)
    return h

#比特串到十六进制
def bits_to_hex(s):
    s_bytes = bits_to_bytes(s)
    s_hex = bytes_to_hex(s_bytes)
    return s_hex

#十六进制串到比特串
def hex_to_bits(h):
    b_list = []
    for i in h:
        b = bin(eval('0x' +i))[2:].rjust(4,'0')
        b_list.append(b)
    b = ''.join(b_list)
    return b

#十六进制到字节串
def hex_to_bytes(h):
    h_bits = hex_to_bits(h)
    h_bytes = bits_to_bytes(h_bits)
    return h_bytes

#域元素到十六进制串
def fielde_to_hex(e):
    h_bytes = fielde_to_bytes(e)
    h = bytes_to_hex(h_bytes)
    return h

#密钥派生函数KDF，接收的参数是比特穿Z和要获得的密钥数据的长度klen,返回klen长度的密钥数据H
def KDF(Z,klen):
    v = 256 #密码杂凑函数采用sm3
    if klen >= (pow(2,32)-1)*v:
        raise Exception(f'密钥派生函数KDF出错，请检查klen的大小!')
    ct = 0x00000001
    if klen % v == 0:
        l = klen //v
    else:
        l = klen//v+1

    Ha = []
    for i in range(l):
        s = Z + int_to_bits(ct).rjust(32,'0')
        s_bytes = bits_to_bytes(s)
        s_list = [i for i in s_bytes]
        hash_hex = sm3.sm3_hash(s_list)
        hash_bin = hex_to_bits(hash_hex)
        Ha.append(hash_bin)
        ct += 1
    if klen % v != 0:
        Ha[-1] = Ha[-1][:klen-v*(klen//v)]
    k = ''.join(Ha)
    return k

#模逆算，返回M模m的逆，在将分式模运算转换为整数是用，分子分母同时乘上分母的模逆
def calc_inverse(M,m):
    if gcd(M,m) != 1:
        return None
    u1,u2,u3 = 1,0,M
    v1,v2,v3 = 0,1,m
    while v3 != 0:
        q = u3 // v3
        v1,v2,v3,u1,u2,u3 = (u1-q*v1),(u2-q*v2),(u3-q*v3),v1,v2,v3
    return u1 % m

#将分式模运算转换为整数，输入up/down mode m,返回该分式在模m意义下的整数，点加和二倍点运算
def frac_to_int(up,down,p):
    num = gcd(up,down)
    up //= num
    down //= num
    return up * calc_inverse(down,p) % p

#椭圆曲线上的点加运算，接收的参数是元组P和Q，表示相加的两个点，p为模数，返回二者的点加和
def add_point(P,Q,p):
    if P == 0:
        return Q
    if Q == 0:
        return P

    x1,y1,x2,y2=P[0],P[1],Q[0],Q[1]
    #e 为lambda
    e = frac_to_int(y2-y1,x2-x1,p)
    x3 = (e*e-x1-x2) % p
    y3 = (e*(x1-x3)-y1) % p
    ans = (x3,y3)
    return ans

#二倍点运算，不能直接用点加算法，否则会发生除零错误，接受的参数是点P，素数p，椭圆曲线参数a
def double_point(P,p,a):
    if P==0:
        return P
    x1,y1 = P[0],P[1]
    # e 为lambda
    e = frac_to_int(3*x1*x1+a,2*y1,p)
    x3 = (e*e-2*x1) % p
    y3 = (e*(x1-x3)-y1) % p
    Q =(x3,y3)
    return Q

#多倍点算法，通过二进制展开发实现，接受的参数[k]p是要求的多倍点，m是模数，a是椭圆曲线参数
def mult_point(P,k,p,a):
    s = bin(k)[2:]#s是k的二进制形式
    Q = 0
    for i in s:
        Q = double_point(Q,p,a)
        if i == '1':
            Q = add_point(P,Q,p)
    return Q

#验证某个点是否在椭圆曲线上，接收的参数是椭圆曲线系统参数args和要验证的点p(x,y)
def on_curve(args,P):
    p,a,b,h,G,n = args
    x,y = P
    if pow(y,2,p) == ((pow(x,3,p)+a*x+b) % p):
        return True
    return False

#椭圆曲线系统参数args(p,a,b,h,G,n)的获取
def get_args():
    # p,a,b用来确定一条椭圆曲线，G为基点，n为点G的阶，h是有限域椭圆曲线上所有点的个数m与n相除得到的整数部分
    p = eval('0x' + '8542D69E 4C044F18 E8B92435 BF6FF7DE 45728391 5C45517D 722EDB8B 08F1DFC3'.replace(' ',''))
    a = eval('0x' + '787968B4 FA32C3FD 2417842E 73BBFEFF 2F3C848B 6831D7E0 EC65228B 3937E498'.replace(' ',''))
    b = eval('0x' + '63E4C6D3 B23B0C84 9CF84241 484BFE48 F61D59A5 B16BA06E 6E12D1DA 27C5249A'.replace(' ',''))
    h = 1
    xG = eval('0x'+'421DEBD6 1B62EAB6 746434EB C3CC315E 32220B3B ADD50BDC 4C4E6C14 7FEDD43D'.replace(' ',''))
    yG = eval('0x'+ '0680512B CBB42C07 D47349D2 153B70C4 E5D7FDFC BFA36EA1 A85841B9 E46E09A2'.replace(' ',''))
    G = (xG,yG)#G是基点
    n = eval('0x'+'8542D69E 4C044F18 E8B92435 BF6FF7DD 29772063 0485628D 5AE74EE7 C32E79B7'.replace(' ',''))
    args = (p,a,b,h,G,n)
    return args

#密钥获取，本程序中主要是消息接收方B的公私钥的获取 ok
def get_key():
    xB = eval('0x'+'435B39CC A8F3B508 C1488AFC 67BE491A 0F7BA07E 581A0E48 49A5CF70 628A7E0A'.replace(' ',''))
    yB = eval('0x'+'75DDBA78 F15FEECB 4C7895E2 C1CDF5FE 01DEBB2C DBADF453 99CCF77B BA076A42'.replace(' ',''))
    PB = (xB,yB)#pb是b的公钥
    # dB = eval('0x'+'1649AB77 A00637BD 5E2EFE28 3FBF3535 34AA7F7C B89463F2 08DDBC29 20BB0DA0'.replace(' ',''))
    dB = eval('0x83afdafdfadfadfd')
    # dB是B的私钥
    key_B = (PB,dB)
    return key_B

# 转换为bytes，第二参数为字节数（可不填）
def to_byte(x, size=None):
    if isinstance(x, int):
        if size is None:  # 计算合适的字节数
            size = 0
            tmp = x >> 64
            while tmp:
                size += 8
                tmp >>= 64
            tmp = x >> (size << 3)
            while tmp:
                size += 1
                tmp >>= 8
        elif x >> (size << 3):  # 指定的字节数不够则截取低位
            x &= (1 << (size << 3)) - 1
        return x.to_bytes(size, byteorder='big')
    elif isinstance(x, str):
        x = x.encode()
        if size != None and len(x) > size:  # 超过指定长度
            x = x[:size]  # 截取左侧字符
        return x
    elif isinstance(x, bytes):
        if size != None and len(x) > size:  # 超过指定长度
            x = x[:size]  # 截取左侧字节
        return x
    elif isinstance(x, tuple) and len(x) == 2 and type(x[0]) == type(x[1]) == int:
        # 针对坐标形式(x, y)
        return to_byte(x[0], size) + to_byte(x[1], size)
    return bytes(x)

# 将data 转换为点，并进行倍点计算
def encrypt(data):
    args = get_args()
    p, a, b, h, G, n = args
    key_B = get_key()
    PB, dB = key_B
    point_temp = bytes_to_point(to_byte(data,31))
    Q = mult_point(point_temp,dB,p,a)
    return Q

# 将第一次倍点计算的结果，进行第二次倍点计算
def dh(Q):
    args = get_args()
    p, a, b, h, G, n = args
    key_B = get_key()
    PB, dB = key_B
    Q = mult_point(Q,dB,p,a)
    return Q

if __name__ == "__main__":
    # temp = encrypt('hea')
    temp = encrypt(1)
    # temp1 = dh(temp)
    print('temp---',temp)
    # print(temp1)
    temp2 = point_to_bytes(temp)
    print('temp2--',temp2)
    temp3 = bytes_to_point(temp2)
    print('temp3----',temp3)