import PythonMagick
import base64


# 生成ico
img = PythonMagick.Image('cmd/image.jfif')
img.sample('256x256')
img.write('cmd/image_256x256.ico')

# 将ico转为base64存于logo.py
open_icon = open("cmd/image_256x256.ico", "rb")
b64str = base64.b64encode(open_icon.read())
open_icon.close()
write_data = "img = %s" % b64str
f = open("logo.py", "w+")
f.write(write_data)
f.close()