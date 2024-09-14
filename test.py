from tinydb import TinyDB, Query

db = TinyDB('db.json')
lead = Query()

res = db.search(lead.id == '!4m7!3m6!1s0x475a6511c6303e3f:0xd559772bf65dfc1!8m2!3d44.8374154!4d20.4027238!16s%2Fg%2F11px31xdn8!19sChIJPz4wxhFlWkcRwd9lv3KXVQ0')

print(res)