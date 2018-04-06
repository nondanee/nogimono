import asyncio
import os, shutil, re, uuid
from PIL import Image
from . import toolbox
from aiohttp import web
# from aiohttp_session import get_session

def delete_file(file_path):
    if file_path: os.remove(file_path)

@asyncio.coroutine
def route(request):

    if request.content_type!="multipart/form-data":
        return toolbox.javaify(400,"content type error")

    try:
        reader = yield from request.multipart()
    except Exception as e:
        print(e)
        return toolbox.javaify(400,"bad request")

    avatar_dir = request.app["avatar_dir"]

    uid = None
    token = None
    temp_path = None
    
    while True:
        try:
            part = yield from reader.next()
        except:
            delete_file(temp_path)
            return toolbox.javaify(400,"bad request")

        if part is None:            
            break

        try:
            key = re.search(r'name="([^"]*)"',part.headers["Content-Disposition"]).group(1)
        except:
            delete_file(temp_path)
            return toolbox.javaify(400,"bad request")

        if key == "uid":
            
            uid = yield from part.text()
            try:
                uid = str(int(uid)).zfill(8)
            except:
                delete_file(temp_path)
                return toolbox.javaify(400,"uid format error")
        
        elif key == "token":
            
            token = yield from part.text()

        elif key == "photo":

            f = None
            size = 0
            
            while True:

                try:
                    chunk = yield from part.read_chunk()  # 8192 bytes by default
                except:
                    return toolbox.javaify(415,"unsupported media type")

                if size == 0 : 

                    if len(chunk) < 4:
                        return toolbox.javaify(400,"bad request")

                    header = ''.join('{:02x}'.format(x) for x in chunk[0:4]).upper()

                    if header[0:6] == 'FFD8FF': #jpg
                        pass
                    elif header[0:8] == '89504E47': #png
                        pass
                    elif header[0:8] == '47494638': #gif
                        pass
                    else:
                        return toolbox.javaify(415,"unsupported media type")

                    temp_path = os.path.join(avatar_dir,str(uuid.uuid1()))
                    f = open(temp_path,'wb')


                if not chunk:
                    f.close()
                    break
                else:
                    size += len(chunk)
                    f.write(chunk)

                if size/1048576 > 3: 
                    f.close()
                    delete_file(temp_path)
                    return toolbox.javaify(413,"entity too large")

        else:
            delete_file(temp_path)
            return toolbox.javaify(400,"unknown argument")


    if not uid or not token or not temp_path:
        delete_file(temp_path)
        return toolbox.javaify(400,"miss argument")

    else:
        with (yield from request.app['pool']) as connect:
            cursor = yield from connect.cursor()
            permit = yield from toolbox.access(cursor,uid,token)
            yield from cursor.close()
            connect.close()

            if not permit:
                delete_file(temp_path)
                return toolbox.javaify(401,"unauthorized")

            user_dir = os.path.join(avatar_dir,uid)
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
                
            os.mkdir(user_dir)

            file_name = "{}.jpg".format(os.path.split(temp_path)[-1])
            file_path = os.path.join(user_dir,file_name)

            try:
                img = Image.open(temp_path)
                img_size = img.size

                if img_size[0] != img_size[1]:
                    delete_file(temp_path)
                    return toolbox.javaify(400,"photo scale error")
                else:
                    img = img.resize((180,180),Image.ANTIALIAS)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(file_path, "JPEG")
                    delete_file(temp_path)
                    # shutil.move(temp_path,file_path)
                    return toolbox.javaify(200,"success",{"avatar":"https://{}/avatar/{}/{}".format(request.app['server_domain'],uid,file_name)})
            
            except:
                return toolbox.javaify(400,"bad request")

            

    
