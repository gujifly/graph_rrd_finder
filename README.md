# graph_rrd_finder
用于 open-falcon，根据 endpoint/counter 字符串，定位出该条监控数据所在的rrd文件位置。
<br>

#### 背景
　　分布式部署了 open-falcon ， 4 个 graph 实例部署在 4 台 服务器， transfer 根据 cluster 名单，
将监控数据按一致性哈希，打向 graph 实例。
<br><br>
　　那么问题来了，如果我要定位 某条监控数据（endpoint/counter） 所在 rrd 文件的具体位置，该怎么查找呢？
<br>

#### 方案
　　阅读了 open-falcon 的 graph 和 transfer 部分源码后，发现其实原理挺简单的。
  
> * rrd 文件名部分： rrd_path = rrd_direct + "/" + md5("endpoint/counter") +"_" + type + "_" + step + ".rrd"
>  * 一致性哈希部分：  node_key = crc32(node_id + node_name)
<br>

一致性哈希实现部分，参考 https://github.com/JustinTulloss/consistentkeys/blob/master/hashring.py

#### 用法

```shell
　　python graph_rrd.py  endpoint0/counter0  endpoint1/counter1 ...
```

#### 输出

![image](https://github.com/gujifly/graph_rrd_finder/blob/master/graph_rrd.png)
