from bottle import TEMPLATE_PATH, run, route, jinja2_template as template
from bottle import post, request, redirect, static_file
import sqlite3 as sq
import json
from random import random, sample
from time import time


TEMPLATE_PATH[:] = ["./templates"]
user_id = '0'
user_age = '0'
user_male = '0'  # 0 for male, 1 for female
question = ''
with open('root.json') as f:
    info = json.load(f)
db = sq.connect(info['dbn'])
cur = db.cursor()
res = {}
row = [0]*12
T1 = time()
T2 = time()
T3 = time()
feedback = 0
admin = False


def logData(dic, net, feed):
    db = sq.connect(info['dbn']+'.db')
    cur = db.cursor()
    v = [()]*info['nt']
    for i in range(1, info['nt']+1):
        v[i-1] = [xx for xx in dic[str(i)] + [net, feed]]
    cur.executemany('insert into ' + info['dbt1'] + ' \
                    values (?, ?, ?, ?, ?, ?, ?, ?,\
                    ?, ?, ?, ?, ?, ?)', v)
    db.commit()
    db.close()
    info['n_users'] = info['n_users']+1
    with open('root.json', 'w') as f:
        json.dump(info, f)


def question_gen():
    global row
    obj = ['line', 'triangle', 'square', 'circle']
    negate = 0
    ls = sample(obj, 2)
    if random() > 0.5:
        negate = 1
        row[7] = 1
    if random() > 0.5:
        row[5] = 1
        question = 'The ' + ls[0] + ' is CHECK above the ' + ls[1]
        if negate:
            question = question.replace('CHECK', 'not')
        else:
            question = question.replace('CHECK ', '')
    else:
        row[6] = 1
        question = 'The ' + ls[0] + ' is CHECK below the ' + ls[1]
        if negate:
            question = question.replace('CHECK', 'not')
        else:
            question = question.replace('CHECK ', '')
    return question


@route('/')
def index():
    return template('home.html')


@route('/admin')
def index_admin():
    global admin
    admin = True
    return template('home.html')


@post('/wap')
def saveStart():
    global user_id
    global user_male
    global user_age
    global feedback
    user_id = info['n_users']
    user_age = request.forms.get('age')
    feedback = request.forms.get('feedback')
    male = int(request.forms.get('sex'))
    row[0] = user_id
    row[1] = user_age
    if male:
        user_male = 1
        row[2] = 1
    else:
        user_male = 0
    redirect('/wap/question/0')
    '''
    ex = 'insert table ' + info['dbt1'] + ' values ('+user_id + ','\
        + user_age + ',' + user_male + ')'
    cur.execute(ex)
    cur.commit()'''


@route('/wap/question/<id>')
def question_show(id):
    global T1
    if int(id) > info['nt']:
        redirect('/wap/network')
    global question
    question = question_gen()
    T1 = time()
    return template('question.html', question=question, id=id)


@route('/wap/pic/<id>')
def pic_show(id):
    global T2
    T2 = time()
    # Triangle
    T = '''<svg height="210" width="500">
    <polygon points="75,10 140,150 5,155"
    style="fill:lime;stroke:purple;stroke-width:1" />
    </svg>'''
    # Square
    S = '''<svg width="500" height="210">
    <rect x="50" y="20" width="150" height="150"
    style="fill:blue;stroke:pink;
    stroke-width:5;fill-opacity:0.1;stroke-opacity:0.9" />
    </svg>'''
    # Line
    L = '''<svg height="210" width="500">
    <line x1="0" y1="0" x2="200" y2="200"
    style="stroke:rgb(255,0,0);stroke-width:2" />
    </svg>'''
    # Circle
    C = '''<svg height="210" width="500">
    <circle cx="120" cy="100" r="55"
    stroke="black" stroke-width="3" fill="red" />
    </svg>'''
    ls = ['']*2
    ti = question.find('triangle')
    ci = question.find('circle')
    si = question.find('square')
    li = question.find('line')
    tup = (ti > -1, ci > -1, si > -1, li > -1)
    if tup == (True, True, False, False):
        if(ti > ci):
            ls = [C, T]
            row[3] = 'circle'
            row[4] = 'triangle'
        else:
            ls = [T, C]
            row[3] = 'triangle'
            row[4] = 'circle'
    elif tup == (True, False, True, False):
        if(ti > si):
            ls = [S, T]
            row[3] = 'square'
            row[4] = 'triangle'
        else:
            ls = [T, S]
            row[3] = 'triangle'
            row[4] = 'square'
    elif tup == (True, False, False, True):
        if(ti > li):
            ls = [L, T]
            row[3] = 'line'
            row[4] = 'triangle'
        else:
            ls = [T, L]
            row[3] = 'trianle'
            row[4] = 'line'
    elif tup == (False, True, True, False):
        if(ci > si):
            ls = [S, C]
            row[3] = 'square'
            row[4] = 'circle'
        else:
            ls = [C, S]
            row[3] = 'circle'
            row[4] = 'square'
    elif tup == (False, True, False, True):
        if(ci > li):
            ls = [L, C]
            row[3] = 'line'
            row[4] = 'circle'
        else:
            ls = [C, L]
            row[3] = 'circle'
            row[4] = 'line'
    elif tup == (False, False, True, True):
        if(li > si):
            ls = [S, L]
            row[3] = 'square'
            row[4] = 'line'
        else:
            ls = [L, S]
            row[3] = 'line'
            row[4] = 'square'
    else:
        print('Unexpected error in pic_show callback')
    inconsistency = 0
    if random() > 0.5:
        inconsistency = 1
        row[8] = 1
    if (row[6] == 1 and row[7] == 0):
        ls = [ls[1], ls[0]]
    if (row[5] == 1 and row[7] == 1):
        ls = [ls[1], ls[0]]
    if inconsistency:
        ls = [ls[1], ls[0]]
    return template('pic.html', shape1=ls[0],
                    shape2=ls[1], id=id)


@post('/wap/rown/<id>')
def save_rown(id):
    global T3
    global row
    T3 = time()
    next = str(int(id)+1)
    accuracy = False
    if row[8] == 1:
        row[9] = 1
        accuracy = True
    row[10] = T2-T1
    row[11] = T3-T2
    res[id] = [xx for xx in row]
    row = [0]*12
    row[0] = user_id
    row[1] = user_age
    row[2] = user_male
    if not feedback:
        redirect('/wap/question/'+next)
    else:
        if accuracy:
            redirect('/wap/feedback1/'+id)
        else:
            redirect('/wap/feedback0/'+id)


@post('/wap/rowy/<id>')
def save_rowy(id):
    global T3
    global row
    T3 = time()
    next = str(int(id)+1)
    accuracy = False
    if row[8] == 0:
        row[9] = 1
        accuracy = True
    row[10] = T2-T1
    row[11] = T3-T2
    res[id] = [xx for xx in row]
    row = [0]*12
    row[0] = user_id
    row[1] = user_age
    row[2] = user_male
    if not feedback:
        redirect('/wap/question/'+next)
    else:
        if accuracy:
            redirect('/wap/feedback1/'+id)
        else:
            redirect('/wap/feedback0/'+id)


@route('/wap/feedback0/<id>')
def feed0_user(id):
    next = str(int(id)+1)
    return template('feedback0.html', next=next)


@route('/wap/feedback1/<id>')
def feed1_user(id):
    next = str(int(id)+1)
    return template('feedback1.html', next=next)


@route('/wap/network')
def networkQuestion():
    return template('network.html')


@route('/wap/finish1')
def saveAlly():
    if admin:
        redirect('/wap/thankyou')
    if feedback:
        logData(res, 1, 1)
    else:
        logData(res, 1, 0)
    redirect('/wap/thankyou')


@route('/wap/finish0')
def saveAlln():
    if admin:
        redirect('/wap/thankyou')
    if feedback:
        logData(res, 0, 1)
    else:
        logData(res, 0, 0)
    redirect('/wap/thankyou')


@route('/wap/thankyou')
def thankyou():
    return template('thankyou.html')


@route('/csv')
def show_csv():
    db = sq.connect(info['dbn']+'.db')
    cur = db.cursor()
    ex = 'select * from '+info['dbt1']+';'
    with open('results.csv', 'w') as f:
        header = '''User_id,Age,Gender,Object1,Object2,Above,Below,Not\
            ,Inconsistency,Accuracy,T1,T2,NeworkSlow,Feedback\n'''
        f.write(header)
        for row in cur.execute(ex):
            st = ','.join([str(xx) for xx in row])+'\n'
            f.write(st)
    db.close()
    with open('results.csv') as f:
        rows = []
        for line in f:
            s = [xx.strip() for xx in line.split(',')]
            rows.append(s)
    return template('results.html', rows=rows)


@route('/results.csv')
def server_static():
    return static_file('results.csv', root='.')


run(host='localhost', port=8080, debug=True)
