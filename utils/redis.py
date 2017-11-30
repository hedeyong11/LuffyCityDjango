# coding:utf-8
# Created by yang


class Redis(object):
    def __init__(self):
        from django_redis import get_redis_connection
        self.conn = get_redis_connection("default")  # Use the name you have defined for Redis in settings.CACHES

    def is_exist(self, key):
        """判断当前的key是否存在于redis中"""
        if self.conn.get(key):
            return True
        return False

    def hset(self, name, key, value):
        """哈希操作
        # name对应的hash中设置一个键值对（不存在，则创建；否则，修改）
        # 参数：
            # name，redis的name
            # key，name对应的hash中的key
            # value，name对应的hash中的value
         
        # 注：
            # hsetnx(name, key, value),当name对应的hash中不存在当前key时则创建（相当于添加）
        """
        self.conn.hset(name, key, value)

    def hget(self,name,key):
        """
        在name对应的hash中获取根据key获取value
        :param key: 
        :return: 返回的是一个字节
        """
        return self.conn.hget(name,key)

    def hexists(self,name, key):
        """
        检查name对应的hash(是一个内存空间,里面存着很多键值对)是否存在 当前传入的key
        可以用来判断,一个用户是否在当前的购物车大列表中
        :param name: 可以写购物车存在于redis中的名,如luffy_cart
        :param key: 可以是用户uid
        :return: 
        """
        return self.conn.hexists(name,key)

    def hdel(self,name,key):
        """
        将name对应的hash中指定key的键值对删除
        :param name: 
        :param keys: 
        :return: 
        """
        self.conn.hdel(name,key)


redis = Redis()

if __name__ == '__main__':
    Redis().is_exist("xxx")
