# 乃木物

介系里没有用过的船新版本  
Python3 & aiohttp & MySQL & Vanilla JS  

## 概览

被消失的多空行和颜文字无意触发markdown解析的问题折磨得死去活来  
有点后悔强上markdown，本来方便的语法规范反而碍手碍脚，一通屏蔽后感觉完全失去价值  
说到底还是自己不可能去造编辑器的轮子，一辈子都不可能的，就只好硬着头皮一通魔改......  

<img src="https://user-images.githubusercontent.com/26399680/38435334-f01e8a30-3a03-11e8-9eca-b95d7341b48b.png" width=100%/>

## 致谢

sparksuite/SimpleMDE (https://github.com/sparksuite/simplemde-markdown-editor)  
Rovak/InlineAttachment (https://github.com/Rovak/InlineAttachment)  
markedjs/marked (https://github.com/markedjs/marked)  

## 接口

>虽然新来的大佬已承包用户系统和评论系统的全部业务，而我只需要把提交平台改进改进，商量着扩展下数据库，平稳过渡旧接口，转换下文本格式给爬虫业务铺垫铺垫就好。
>
>不过自己还是花了些时间实现了评论和回复，一是因为从来没做过评论，有些复杂挺有挑战性想试试，二是因为我有我自己的想法。确实合作开发的分歧会比较多，何况语言不一样，习惯也不一样。
>
>也不知道大佬是怎么优雅地实现的，我用JOIN嵌了三层，还有个循环查库，删除那个感觉还递归了，开销巨大但是没有办法。都怪自己没太菜，不会用框架就只能强行写语句......

使用请求Headers中的`uid`和`token`字段验证身份  
POST请求内容类型指定为`application/x-www-form-urlencoded`  
返回数据格式均为  
```
{
    "code": ???,
    "data": ???,
    "message": "???"
}
```  
以下只说明有效请求的data部分  

### 创建评论 

POST `/api/comment`

```
fid={文章ID}&message={评论内容}
```

### 删除评论 

DELETE `/api/comment`

```
cid={评论ID}
```


### 评论列表
GET `/api/comment`

```
?fid={文章ID}&page={页码从1开始}
```

```
[
    {
        "author": {
            "avatar": 头像链接,
            "id": 用户ID,
            "nickname": 用户昵称
        },
        "children": [
            {
                "author": {
                    "avatar": 头像链接,
                    "id": 用户ID,
                    "nickname": 用户昵称
                },
                "floor": 副评论所在楼层,
                "id": 评论ID,
                "message": 评论文字,
                "post": 时戳
            },
            ... //每个主评论最多显示5条副评论，时间倒序
        ],
        "floor": 主评论所在楼层,
        "id": 评论ID,
        "message": 评论文字,
        "post": 时戳
    },
    ... //一页10条主评论，时间倒序
]
```

### 创建回复

POST `/api/reply`

```
cid={评论ID}&message={回复内容}
```


### 回复列表
GET `/api/reply`

```
?cid={主评论ID}&page={页码从1开始}
```

```
{
    "author": {
        "avatar": 头像链接,
        "id": 用户ID,
        "nickname": 用户昵称
    },
    "children": [
        {
            "author": {
                "avatar": 头像链接,
                "id": 用户ID,
                "nickname": 用户昵称
            },
            "floor": 副评论所在楼层,
            "id": 评论ID,
            "message": 评论文字,
            "post": 时戳
        },
        ... //一页10条副评论，时间倒序，主评论内容每页都返回
    ],
    "floor": 主评论所在楼层,
    "id": 评论ID,
    "message": 评论文字,
    "post": 时戳
}
```

### 通知列表

GET `/api/notification`

```
?page={页码从1开始}
```

```
[
    {
        "author": {
            "avatar": 头像链接,
            "id": 用户ID,
            "nickname": 用户昵称
        },
        "fid": 文章ID,
        "floor": 评论所在楼层,
        "id": 评论ID,
        "message": 评论文字,
        "origin": {
            "floor": 自己的评论所在楼层,
            "id": 自己的评论ID,
            "message": 自己的评论文字,
            "post": 时戳
        },
        "post": 时戳,
        "root": 所在主评论ID，
        "unread": 未读标记
    },
    ... //一页10条通知，时间倒序
]
```

