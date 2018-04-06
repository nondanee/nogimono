import asyncio
from aiohttp import web
from aiohttp_session import get_session

html = '''
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>乃木物</title>
	<style type="text/css">
	html,body{margin: 0;font-family: Microsoft YaHei;}
	#name{font-size: 48px;font-weight: bold;padding: 2px 0;color: #555;}
	form{position: absolute;width: 360px;height: 320px;left: 0;right: 0;top: 0;bottom: 0;margin: auto;}
	input,button{display: block;width: 100%;box-sizing: border-box;padding: 10px;margin: 8px 0;border: 1px solid #ddd;border-radius: 4px;font-size: 16px;height: 44px;color: #555;}
	button{background-color: #eee;font-size: 18px;line-height: 18px;cursor: pointer;}
	#message{margin-top: 12px;text-align: center;color: red;}
	</style>
</head>
<body>
	<form>
		<div id="name">NOGIMONO</div>
		<input id="nickname" type="text" autocomplete="no" placeholder="用户名">
		<input id="password" type="password" autocomplete="off" placeholder="密码">
		<button id="submit" type="button">登录</button>
		<div id="message"></div>
	</form>
</body>
<script type="text/javascript">
const regexp =new RegExp("^[\\d|a-z|_]+?@[\\d|a-z|_]+?\\.[\\d|a-z|_|.]+?$","g")
const nicknameInput = document.getElementById("nickname")
const passwordInput = document.getElementById("password")
const submitButton = document.getElementById("submit")
const messageBox = document.getElementById("message")
function showMessage(message){
	messageBox.innerHTML = message
	setTimeout(function(){messageBox.innerHTML = ""},1800)
}
submitButton.onclick = function(){
	// if(emailInput.value==""||passwordInput.value==""){return}
	let nickname = nicknameInput.value
	let password = passwordInput.value
	// if(regexp.test(email)==false){
	// 	showMessage("请输入正确格式的邮箱地址")
	// 	return
	// }
	let xhr = new XMLHttpRequest()
	let postData = "nickname="+nickname+"&password="+password;
	xhr.onreadystatechange=function(){
		if(xhr.readyState==4){
			if(xhr.status==200){
				window.location = "/home"
			}
			else{
				showMessage("用户名或密码不正确")
			}
		}
	}
	xhr.open('POST',"/user/login",true)
	xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
	xhr.send(postData)
}
</script>
</html>
'''

@asyncio.coroutine
def route(request):

    session = yield from get_session(request)
    if 'uid' not in session:
        return web.Response(
            text = html,
            content_type = 'text/html',
            charset = 'utf-8'
        )
    else:
    	return web.HTTPFound('/home')
