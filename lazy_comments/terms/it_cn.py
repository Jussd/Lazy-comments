# -*- coding: utf-8 -*-
"""
ZH -> EN 编程与IT开发方言字典 (Китайский IT / дев-сленг).

Особенности:
- Учтено отсутствие пробелов в китайском языке (регулярные выражения без границ слов).
- Включены сленговые дев-иероглифы (提, 推, 拉, 切).
- Добавлены частые фонетические искажения китайских STT-движков (瑞艾克特, 吉特哈布, 叶森).
"""

import re

TERMS = {
    # 1. 高级短语与架构 (Сложные фразы и конструкции)
    '面向对象编程': 'object-oriented programming',
    '命令行界面': 'command line interface',
    '环境变量': 'environment variable',
    '正则表达式': 'regular expression',
    '返回布尔值': 'returns boolean',
    '返回字符串': 'returns string',
    '返回整数': 'returns integer',
    '返回对象': 'returns object',
    '返回数组': 'returns array',
    '双向链表': 'doubly linked list',
    '单向链表': 'singly linked list',
    '打印到控制台': 'console.log',
    '打印控制台': 'console.log',
    '响应式设计': 'responsive design',
    '高阶函数': 'higher-order function',
    '解构赋值': 'destructuring',
    '集成测试': 'integration test',
    '单元测试': 'unit test',
    '自动化测试': 'automated test',
    '端到端测试': 'end-to-end test',
    '数据持久化': 'data serialization',
    '前后端分离': 'frontend-backend separation',
    '高并发': 'high concurrency',
    '内存泄漏': 'memory leak',
    '依赖注入': 'dependency injection',

    # 2. 核心动词与开发俚语 (Глаголы и дев-сленг действий)
    '重构': 'refactor',
    '调试': 'debug',
    '回滚': 'rollback',
    '解析': 'parse',
    '克隆': 'clone',
    '编译': 'compile',
    '构建': 'build',
    '部署': 'deploy',
    '发布': 'release',
    '初始化': 'initialize',
    '实例化': 'instantiate',
    '序列化': 'serialize',
    '反序列化': 'deserialize',
    '异步处理': 'async processing',
    '拉取请求': 'pull request',
    '强制推送': 'force push',
    
    # Односимвольный дев-сленг (крайне популярен в чатах)
    '提代码': 'commit',
    '推代码': 'push',
    '拉代码': 'pull',
    '切分支': 'switch branch',
    '删分支': 'delete branch',
    '合代码': 'merge code',
    '上生产品': 'deploy to production',
    '修感冒': 'fix bug',  # шутливый сленг (лечить простуду/баг)

    # 3. 语音识别音译与变形 (Фонетические искажения и транслитерации для STT)
    '扎瓦斯克里普特': 'JavaScript',
    '爪哇脚本': 'JavaScript',
    '泰普史翠普': 'TypeScript',
    '瑞艾克特': 'React',
    '雷阿克特': 'React',
    '芮阿克': 'React',
    '吉特哈布': 'GitHub',
    '鸡塔布': 'GitHub',
    '吉特拉博': 'GitLab',
    '德普洛伊': 'deploy',
    '迪普洛伊': 'deploy',
    '埃斯克尔': 'SQL',
    '艾斯奎尔': 'SQL',
    '格拉夫奎尔': 'GraphQL',
    '安古拉': 'Angular',
    '安古勒': 'Angular',
    '斯普林': 'Spring',
    '多克': 'Docker',
    '库伯内蒂斯': 'Kubernetes',
    '叶森': 'JSON',
    '杰森': 'JSON',
    '皮阿': 'PR',
    '阿普': 'App',
    '巴肯': 'backend',
    '弗朗特恩': 'frontend',
    '维埃斯扣德': 'VS Code',
    '巴格': 'bug',

    # 4. 名词、组件与概念 (Существительные, компоненты и концепты)
    '面向对象': 'object-oriented',
    '函数式': 'functional',
    '副作用': 'side effect',
    '私钥': 'private key',
    '公钥': 'public key',
    '用户界面': 'user interface',
    '源代码': 'source code',
    '数据库': 'database',
    '中间件': 'middleware',
    '服务端': 'server-side',
    '客户端': 'client-side',
    '路由': 'route',
    '路由器': 'router',
    '请求': 'request',
    '响应': 'response',
    '请求头': 'headers',
    '代码仓': 'repository',
    '仓库': 'repository',
    '依赖包': 'package',
    '依赖': 'dependency',
    '循环': 'loop',
    '分支': 'branch',
    '线程': 'thread',
    '进程': 'process',
    '文件': 'file',
    '文件夹': 'folder',
    '目录': 'directory',
    '对象': 'object',
    '类': 'class',
    '函数': 'function',
    '方法': 'method',
    '接口': 'interface',
    '异常': 'exception',
    '参数': 'parameter',
    '实参': 'argument',
    '实例': 'instance',
    '继承': 'inheritance',
    '多态': 'polymorphism',
    '封装': 'encapsulation',
    '字典': 'dictionary',
    '列表': 'list',
    '集合': 'set',
    '元组': 'tuple',
    '控制台': 'console',
    '配置文件': 'config file',
    '令牌': 'token',
    '容器': 'container',
    '生产环境': 'production',
    '开发环境': 'development',

    # 5. 编程关键字与短标记 (Ключевые слова и маркеры)
    '布尔': 'boolean',
    '整数': 'integer',
    '浮点数': 'float',
    '字符串': 'string',
    '数组': 'array',
    '空': 'null',
    '如果是': 'if',
    '如果': 'if',
    '否则如果': 'else if',
    '否则': 'else',
    '遍历': 'forEach',
    '返回': 'return',
    '中断': 'break',
    '跳出': 'break',
    '继续': 'continue',
    '尝试': 'try',
    '捕获': 'catch',
    '抛出': 'throw',
    '常量': 'const',
    '变量': 'variable',
    '等于': 'equal',
    '不等于': 'not equal',
    '大于': 'greater',
    '小于': 'less',
    '逻辑与': 'and',
    '逻辑或': 'or',
    '逻辑非': 'not',
    '连接': 'join',
    '错误': 'error',
    '日志': 'logs',
}

def translate(text: str) -> str:
    """Заменяет китайский IT-сленг на английские термины (без учета границ слов \b)."""
    result = text
    # Сортировка по длине критически важна для китайского языка.
    # Сначала заменяются длинные фразы ('面向对象编程'), затем их части ('面向对象', '编程').
    for term in sorted(TERMS, key=len, reverse=True):
        # Используем re.escape, чтобы спецсимволы в ключах не ломали регулярку.
        # Флаг re.IGNORECASE нужен для англоязычных вставок внутри китайского текста.
        result = re.sub(re.escape(term), TERMS[term], result, flags=re.IGNORECASE)
    return result

if __name__ == "__main__":
    # Тестовый пример, имитирующий сленговую речь китайского разработчика:
    sample = "快打开那个雷阿克特项目，把分支切至main，拉代码然后提代码到吉特哈布仓"
    print(translate(sample))
    # Ожидаемый вывод: "快打开那个React项目，把branch切至main，pull然后commit到GitHub仓"