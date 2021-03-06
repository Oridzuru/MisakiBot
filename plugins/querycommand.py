import nonebot
from nonebot import on_command, CommandSession
import sqlite3


# 各一次性档线查询接口
@on_command('event', only_to_me=False, aliases=('档线', '活动档线', '档线查询', '当前档线', 'pt档线'))
async def event(session: CommandSession):
    sqlconn = sqlite3.connect('Misaki.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT * FROM GlobalVars where VarName = ? LIMIT 1', ('str_ptnew',))
    values = result.fetchall()
    if len(values) > 0:
        await session.send(str(values[0][1]))
    else:
        await session.send('未找到数据。')


@on_command('highscore', only_to_me=False, aliases=('高分档线', '高分', '高分查询', '活动曲档线', '活动曲排行'))
async def event(session: CommandSession):
    sqlconn = sqlite3.connect('Misaki.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT * FROM GlobalVars where VarName = ? LIMIT 1', ('str_hsnew',))
    values = result.fetchall()
    if len(values) > 0:
        await session.send(str(values[0][1]))
    else:
        await session.send('未找到数据。')

@on_command('match', only_to_me=False, aliases=('档线对比', '增幅对比', '档线趋势', '趋势比较'))
async def event(session: CommandSession):
    sqlconn = sqlite3.connect('Misaki.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT * FROM GlobalVars where VarName = ? LIMIT 1', ('str_ptcomp',))
    values = result.fetchall()
    if len(values) > 0:
        await session.send(str(values[0][1]))
    else:
        await session.send('未找到数据。')

@on_command('predict', only_to_me=False, aliases=('档线预测', '预测档线', '预测查询', '活动预测', ''))
async def event(session: CommandSession):
    sqlconn = sqlite3.connect('Misaki.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT * FROM GlobalVars where VarName = ? LIMIT 1', ('str_predict',))
    values = result.fetchall()
    if len(values) > 0:
        await session.send(str(values[0][1]))
    else:
        await session.send('未找到数据。')


# 历史档线查询，根据关键字查找最多3个活动
@on_command('eventhis', only_to_me=False, aliases=('历史档线', '历史活动', '历史pt', '历史查询', '历史'))
async def eventhis(session: CommandSession):
    typename = {3: '传统', 4: '巡演'}
    word = session.get('str')
    sqlconn = sqlite3.connect('Misaki.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT ID, Name, Type, BeginTime, EndTime, BoostStart FROM EventInfo where ID = ? OR \
        Name like ? LIMIT 3', (word, '%'+word+'%'))
    values = result.fetchall()
    resultstr = ''
    if len(values) == 0:
        resultstr += '未得到结果，请确认关键字输入正确（必须是官方活动名称的一部分，暂不支持各种玩家间\
        约定俗成的缩写）。暂无扩线前的数据，正在寻找补充途径。'
    for j in values:
        resultstr += '活动名称: ' + str(j[1]) + '\n类型: ' + typename[j[2]] + \
                    '\n开始时间: ' + str(j[3]) + '\n结束时间: ' + str(j[4]) +\
                     '\n折返时间: ' + str(j[5]) + '\n' +\
                     '=======================\n'+ '\t档线\t\t分数\n'
        resultstr = checkevent(sqlcursor, j[0], resultstr)
    await session.send(resultstr)


@eventhis.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg:
       session.state['str'] = stripped_arg
    else:
        session.finish('格式错误，请使用活动序号或活动的部分关键字来查询。\n例:【历史档线 100】或【历史活动档线 君花火】')


def checkevent(cursor, id, resultstr):
    result = cursor.execute("select Rank, EventPT, PTIncrease from Eventhistory where EventID = ? and Time = \
    (select max(time) from EventHistory where EventID = ?) ORDER BY Rank", (id, id, ))
    values = result.fetchall()
    for j in values:
        resultstr += '\t' + str(j[0]) + ':\t\t' + str(j[1]) + '(+' + str(j[2]) + ')\n'
    resultstr += '\n'
    return resultstr


@on_command('highscorehis', only_to_me=False, aliases=('历史高分', '历史高分查询', '历史高分档线', '历史活动曲档线'))
async def highscorehis(session: CommandSession):
    typename = {3: '传统', 4: '巡演'}
    word = session.get('str')
    sqlconn = sqlite3.connect('Misaki.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT ID, Name, Type, BeginTime, EndTime, BoostStart FROM EventInfo where ID = ? OR \
        Name like ? LIMIT 3', (word, '%'+word+'%'))
    values = result.fetchall()
    resultstr = ''
    for j in values:
        resultstr += '活动名称: ' + str(j[1]) + '\n类型: ' + typename[j[2]] + \
                    '\n开始时间: ' + str(j[3]) + '\n结束时间: ' + str(j[4]) +\
                     '\n折返时间: ' + str(j[5]) + '\n'+\
                     '=======================\n'+ '\t档线\t\t分数\n'
        resultstr = checkhs(sqlcursor, j[0], resultstr)
    await session.send(resultstr)


@highscorehis.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg:
        session.state['str'] = stripped_arg
    else:
        session.finish('格式错误，请使用活动序号或活动的部分关键字来查询。\n例:【历史高分 100】或【历史高分档线 HARMONY】')


def checkhs(cursor, id, resultstr):
    result = cursor.execute("select Rank, HighScore from EventHighscore where EventID = ? and Time = \
    (select max(time) from EventHighscore where EventID = ?) ORDER BY Rank", (id, id, ))
    values = result.fetchall()
    for j in values:
        resultstr += '\t' + str(j[0]) + ':\t \t' + str(j[1]) + '\n'
    resultstr += '\n'
    return resultstr
