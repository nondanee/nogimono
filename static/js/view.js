var renderer = new marked.Renderer()
var status = 'cn'
renderer.code = function(code){
	return code.replace(/&lt;br&gt;/g,"<br>")
}
renderer.codespan = function(code){
	return code.replace(/&lt;br&gt;/g,"<br>")
}

function timeFormat(timeStamp){
	var date = new Date(timeStamp*1000)
	var year = date.getFullYear().toString()
	var month = (date.getMonth() + 1).toString()
	var day = date.getDate().toString()
	var hour = date.getHours().toString()
	var minute = date.getMinutes()
	month = (month < 10) ? '0' + month.toString() : month.toString()
	day = (day < 10) ? '0' + day.toString() : day.toString()
	hour = (hour < 10) ? '0' + hour.toString() : hour.toString()
	minute = (minute < 10) ? '0' + minute.toString() : minute.toString()
	if(hour == '0' || minute == '00')
		return `${year}-${month}-${day}`
	else
		return `${month}-${day} ${hour}:${minute}`
}
function createElement(tagName,className=""){
	var element = document.createElement(tagName)
	element.className = className
	return element
}
function build(){
	var fragment = document.createDocumentFragment()
	var block = createElement('div','block')
	var title = createElement('div','title')
	title.classList.add(status)

	if(shareData.raw){
		title.onclick = function(){
			status = (status == 'cn') ? 'jp' : 'cn'
			build()
		}
	}

	var provider = createElement('div','provider')
	var avatar = createElement('div','avatar')
	avatar.style.backgroundImage = `url(${shareData.provider.avatar})`
	var detail = createElement('div','detail')
	var name = createElement('div','name')
	name.innerHTML = shareData.provider.name
	var introduction = createElement('div','introduction')
	introduction.innerHTML = shareData.provider.introduction
	provider.appendChild(avatar)
	detail.appendChild(name)
	detail.appendChild(introduction)
	provider.appendChild(detail)
	
	var article = createElement('div','article')
	if(status == 'cn'){
		title.innerHTML = shareData.title
		article.innerHTML = marked(shareData.article.replace(/\n/g,'<br>'),{renderer: renderer})		
	}
	else{
		title.innerHTML = shareData.subtitle
		article.innerHTML = marked(shareData.raw.replace(/\n/g,'<br>'),{renderer: renderer})
	}

	var delivery = createElement('div','delivery')
	delivery.innerHTML = timeFormat(shareData.post)

	fragment.appendChild(title)
	fragment.appendChild(provider)
	fragment.appendChild(article)
	fragment.appendChild(delivery)
	document.body.innerHTML = ''
	document.body.appendChild(fragment)
}
document.addEventListener('DOMContentLoaded',function(){
	build()
},false)
