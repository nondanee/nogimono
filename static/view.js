var rendererMD = new marked.Renderer()
rendererMD.code = function(code){
	return code.replace(/&lt;br&gt;/g,"<br>")
}
rendererMD.codespan = function(code){
	return code.replace(/&lt;br&gt;/g,"<br>")
}
function timeFormat(timeStamp){
	var date = new Date(timeStamp*1000)
	var month = (date.getMonth() + 1).toString()
	var day = date.getDate().toString()
	var hour = date.getHours().toString()
	var minute = date.getMinutes()
	minute = (minute < 10) ? "0"+minute.toString() : minute.toString()
	var timeInfo = month + "/" + day + " " + hour + ":" + minute
	return timeInfo
}
function startUp(shareData){
	var fragment = document.createDocumentFragment()
	var block = document.createElement('div')
	block.className = "block"
	var title = document.createElement('div')
	title.className = "title"
	title.innerHTML = shareData.title
	var subtitle = document.createElement('div')
	subtitle.className = "subtitle"
	subtitle.innerHTML = shareData.subtitle
	var post = document.createElement('div')
	post.className = "post"
	var provider = document.createElement('div')
	provider.className = "provider"
	provider.innerHTML = shareData.provider
	var delivery = document.createElement('div')
	delivery.className = "delivery"
	delivery.innerHTML = timeFormat(shareData.post)
	var article = document.createElement('div')
	article.className = "article"
	article.innerHTML = marked(shareData.article.replace(/\n/g,'<br>'),{renderer: rendererMD})
	block.appendChild(title)
	block.appendChild(subtitle)
	post.appendChild(provider)
	post.appendChild(delivery)
	fragment.appendChild(block)
	fragment.appendChild(post)
	fragment.appendChild(article)
	document.body.appendChild(fragment)
}
document.addEventListener('DOMContentLoaded',function(){
     startUp(shareData)
},false)
