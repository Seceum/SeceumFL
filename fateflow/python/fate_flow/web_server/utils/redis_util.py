import redis

from fate_flow.web_server.fl_config import config
from fate_flow.utils.log_utils import LoggerFactory, getLogger
fate_redis_logger = getLogger("fate_redis")
def operator_status(func):
    def gen_status(*args,**kwargs):
        error ,result = None,None
        try:
            result = func(*args,**kwargs)
        except Exception as e:
            error=str(e)
            fate_redis_logger.error(e)
        return result,error
    return gen_status

class Redis_db():
    def __init__(self):
        if not hasattr(Redis_db,"pool"):
            Redis_db.create_pool()
        if hasattr(Redis_db,"pool"):
            self.conn = redis.Redis(connection_pool=Redis_db.pool)


    @staticmethod
    def create_pool():
        redis_host = config.cf["redis"]["redis_host"]
        redis_port = config.cf["redis"]["redis_port"]
        redis_pwd = config.cf["redis"]["redis_pwd"]
        redis_socket_db = config.cf["redis"]["redis_socket_db"]
        try:
            rs =redis.Redis(host=redis_host,port=redis_port,password=redis_pwd,socket_timeout =1 ,socket_connect_timeout=1)
            rs.ping()
            del rs
            Redis_db.pool= redis.ConnectionPool(host=redis_host,port=redis_port,password=redis_pwd,db=redis_socket_db,decode_responses=True)
        except Exception as e:
            fate_redis_logger.error(e)

    @operator_status
    def hset(self,key,field,value,expire=None):
        res = self.conn.hset(key,field,value)
        if expire:
            self.conn.expire(key,expire)
        return res

    @operator_status
    def hget(self,key):
        return self.conn.hgetall(key)

    @operator_status
    def hdel(self, key,field):
        return self.conn.hdel(key,field)

if __name__ == '__main__':

    redis_db = Redis_db()
    res,error =redis_db.hset("users_query1","a","abc",expire=10)
    # res,error =redis_db.hset("users_query1","b","abc")
    # res =redis_db.hdel("users_query1","a")
    res,error =redis_db.hget("users_query1")
    print(res, error)
    # if users_query is None:
    #     print("users_query",None)
    # print(type(users_query))
    # print("res",users_query)
