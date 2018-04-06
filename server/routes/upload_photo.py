import asyncio
import os, random, time, hashlib
from . import toolbox
from aiohttp import web
from aiohttp_session import get_session

@asyncio.coroutine
def route(request):

    session = yield from get_session(request)
    if 'uid' in session:
        uid = session['uid']
    else:
        return web.HTTPForbidden()

    query_parameters = request.rel_url.query
    try:
        fid = int(query_parameters["fid"])
        fid = str(fid).zfill(8)
    except:
        return web.HTTPBadRequest()

    if request.content_type!="multipart/form-data":
        return web.HTTPBadRequest()

    try:
        reader = yield from request.multipart()
    except Exception:
        return web.HTTPBadRequest()

    next = yield from reader.next()

    photo_dir = os.path.join(request.app["photo_dir"],fid)

    if os.path.exists(photo_dir)==0:
        os.mkdir(photo_dir)

    size = 0
    suffix = ''
    hash_calc = hashlib.md5()
    
    while True:
        try:
            chunk = yield from next.read_chunk()  # 8192 bytes by default
        except Exception:
            return web.HTTPBadRequest()

        if not chunk:
            break

        if size == 0 : 

            if len(chunk) < 4:
                return web.HTTPBadRequest()
 
            top_eight_bytes=''.join('{:02x}'.format(x) for x in chunk[0:4]).upper()

            if top_eight_bytes[0:6] == 'FFD8FF':
                suffix = "jpg"
            elif top_eight_bytes[0:8] == '89504E47':
                suffix = "png"
            elif top_eight_bytes[0:8] == '47494638':
                suffix = "gif"
            else:
                return web.HTTPBadRequest()

            while True:
                temp_name = str(int(time.time())) + str(random.randint(0,9999)).zfill(4)
                temp_file = os.path.join(photo_dir,temp_name)
                if not os.path.exists(temp_file):
                    break
                
            file = open(temp_file,'wb')

        size = size + len(chunk)      
        file.write(chunk)
        hash_calc.update(chunk)

        if size / 1048576 > 2: # size limit 2MB
            file.close()
            os.remove(temp_file)
            return web.HTTPRequestEntityTooLarge()

    file.close()
    hash_value = hash_calc.hexdigest()
    formal_name = hash_value + "." + suffix
    formal_file = os.path.join(photo_dir,formal_name)

    if os.path.exists(formal_file) != 0:
        os.remove(temp_file)
    else:
        os.rename(temp_file, formal_file)


    # with (yield from request.app['pool']) as connect:

    #    cursor = yield from connect.cursor()

    #    try:
    #        yield from cursor.execute('''
    #            INSERT INTO photo VALUES(%s,%s,%s,%s) 
    #        ''',(hash_value,fid,suffix,0))
    #        yield from connect.commit()
    #    except Exception as e:
    #        print(e)

    #    yield from cursor.close()
    #    connect.close()
        
    return web.Response(
        text = toolbox.jsonify({"filename": formal_name}),
        # headers = {'Access-Control-Allow-Origin':'*'}
    )
