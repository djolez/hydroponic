import os
from datetime import *

start = datetime.now() - timedelta(hours=3)
end = datetime.now()

imgs = (os.path.join('../web-app/img/timelapse', fn) for fn in os.listdir('../web-app/img/timelapse'))
imgs = ((os.stat(path), path) for path in imgs)

def get_key(item):
    return item[0][8]

res = []

for i in sorted(imgs, key=get_key):
    created = datetime.fromtimestamp(i[0][8])

    if start <= created <= end:
        res.append(os.path.basename(i[1]))
        print(os.path.basename(i[1]))

'''@app.route('/camera/open-timelapse')
def list_timelapse():
    
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d %H:%M:%S') if 'start_date' in request.args else (datetime.now() - timedelta(hours=3))
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d %H:%M:%S') if 'end_date' in request.args else datetime.now()
 
    imgs = (os.path.join('../web-app/img/timelapse', fn) for fn in os.listdir('../web-app/img/timelapse'))
    imgs = ((os.stat(path), path) for path in imgs)

    def get_key(item):
        return item[0][8]

    res = []

    for i in sorted(imgs, key=get_key):
        created = datetime.fromtimestamp(i[0][8])

        if start <= created <= end:
            res.append(i[1])

    return jsonify({'data': res})
'''
