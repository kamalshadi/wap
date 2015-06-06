import sqlite3 as sq
import os
import json


# Delete all previous tables and datasets
def reset():
    # Global variables
    with open('root.json') as f:
        info = json.load(f)
    dbn = info['dbn']
    dbt1 = info['dbt1']
    if os.path.isfile(dbn+'.db'):
        os.remove(dbn+'.db')
    db = sq.connect(dbn+'.db')
    cur = db.cursor()
    ex1 = 'create table '+dbt1+' (id integer,\
        age INTEGER, gender integer, obj1 text, obj2 text,\
        above integer, below integer, negate integer, pic iteger,\
        accuray iteger, T1 real, T2 real,\
        network integer, feedback integer)'
    cur.execute(ex1)
    db.commit()
    db.close()
    info['n_users'] = 0
    with open('root.json','w') as f:
        json.dump(info, f)
