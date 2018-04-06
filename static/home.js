const createButton = document.getElementById("create")
const submitButton = document.getElementById("submit")
const titleInput = document.getElementById("title")
const subtitleInput = document.getElementById("subtitle")
const typeInput = document.getElementById("type")
const articleInput = document.getElementById("article")
const feedGallery = document.getElementById("feed")


let fidWorking = null
let fidPrepared = null
let simpleMDE = null


let rendererMD = new marked.Renderer()
rendererMD.image = function(href, title, text){
	if (/[0-9|a-z]{32}\.(jpg|png|gif)/.test(href))
		return `<img src="/photo/${fidWorking}/${href}" alt="${text}">`;
	else
		return `<img src="{href}" alt="${text}">`;
}
rendererMD.code = function(code){
	return code.replace(/&lt;br&gt;/g,"<br>")
}
rendererMD.codespan = function(code){
	return code.replace(/&lt;br&gt;/g,"<br>")
}

simpleMDEConfig = { 
	element: articleInput,
	placeholder: "文本",
	spellChecker: false,
	// toolbar: false,
	// hideIcons: ["link", "image", "guide"],
	previewRender: function(plainText) {
		return marked(plainText.replace(/\n/g,'<br>'),{renderer: rendererMD});
	},
	toolbar: [
		{
			name: "bold",
			action: SimpleMDE.toggleBold,
			className: "fa fa-bold",
			title: "Bold",
		},
		{
			name: "italic",
			action: SimpleMDE.toggleItalic,
			className: "fa fa-italic",
			title: "Italic",
		},
		"|",
		{
			name: "link",
			action: SimpleMDE.drawLink,
			className: "fa fa-link",
			title: "Create Link",
		},
		{
			name: "image",
			action: function customFunction(editor){
				let fileInput = document.createElement("input")
				fileInput.setAttribute("type","file")
				fileInput.setAttribute("accept","image/*")
				fileInput.onchange = function () { 
					if(this.files[0]){
						uploadFile(this.files[0],function(filename){
							console.log(filename)
							editor.codemirror.replaceSelection(`![](${filename})`)
							fileInput.value = ''
						})
					}
				}
				fileInput.click()
			},
			className: "fa fa-picture-o",
			title: "Insert Image",
		},
		"|",
		{
			name: "preview",
			action: SimpleMDE.togglePreview,
			className: "fa fa-eye no-disable",
			title: "Toggle Preview",
		},
		{
			name: "side-by-side",
			action: SimpleMDE.toggleSideBySide,
			className: "fa fa-columns no-disable no-mobile",
			title: "Toggle Side by Side",
		},
		{
			name: "fullscreen",
			action: SimpleMDE.toggleFullScreen,
			className: "fa fa-arrows-alt no-disable no-mobile",
			title: "Toggle Fullscreen",
		}
	]
}


function uploadFile(file,callBack){
	let formData = new FormData()
	formData.append("file",file)
	let xhr = new XMLHttpRequest()
	xhr.onreadystatechange = function(){
		if(xhr.readyState == 4){
			if(xhr.status == 200){
				callBack(JSON.parse(xhr.responseText).filename)
			}
		}
	}
	xhr.open("POST","/upload/photo?fid="+fidWorking)
	xhr.send(formData)
}

function attachment() {
	simpleMDE.toTextArea()
	simpleMDE = new SimpleMDE(simpleMDEConfig)
	inlineAttachment.editors.codemirror4.attach(simpleMDE.codemirror, {
		uploadUrl: "/upload/photo?fid="+fidWorking,
		progressText: "![图片上传中...]()",
		urlText:'![]({filename})',
	});
}


function timeFormat(date){
	date = new Date(date)
	let year = date.getFullYear().toString()
	let month = (date.getMonth() + 1).toString()
	let day = date.getDate().toString()
	let hour = date.getHours().toString()
	let minute = date.getMinutes()
	minute = (minute < 10) ? "0"+minute.toString() : minute.toString()
	let timeinfo = year + "." + month + "." + day + " " + hour + ":" + minute
	return timeinfo
}

function resetCardStyle(){
	cards = feedGallery.getElementsByClassName("focus")
	for(let i=0;i<cards.length;i++){
		cards[i].classList.remove("focus")
	}
}

function Feed(feedGallery){
	let loading = false
	let page = 1
	let end = false

	function loadMore(){
		if (loading||end)
			return
		else
			loading = true
		let xhr = new XMLHttpRequest()
		xhr.onreadystatechange=function(){
			if(xhr.readyState==4){
				if(xhr.status==200){
					let jsonBack = JSON.parse(xhr.responseText)
					let fragment = document.createDocumentFragment()
					for(var i = 0;i<jsonBack.length;i++){
						fragment.appendChild(buildCard(jsonBack[i]))
					}
					feedGallery.appendChild(fragment)
					page = page + 1
					if (jsonBack.length == 0)
						end = true
				}
				loading = false
			}
		}
		xhr.open('GET',"/archive/feed?page="+page,true)
		xhr.send()
	}

	feedGallery.onscroll = function(){
		if (this.scrollHeight - 120 < this.scrollTop + this.offsetHeight) {
			loadMore()
		}
	}

	loadMore()

}


function createArticle(callBack){
	let xhr = new XMLHttpRequest()
	xhr.onreadystatechange=function(){
		if(xhr.readyState==4){
			if(xhr.status==200){
				let jsonBack = JSON.parse(xhr.responseText)
				fidPrepared = jsonBack["fid"]
				callBack()
			}
		}
	}
	xhr.open('POST',"/upload/create",true)
	xhr.send()
}

function openArticle(id){
	let xhr = new XMLHttpRequest()
	xhr.onreadystatechange=function(){
		if(xhr.readyState==4){
			if(xhr.status==200){
				let jsonBack = JSON.parse(xhr.responseText)
				fillInput(jsonBack.title,jsonBack.subtitle,jsonBack.type,jsonBack.article)
				fidWorking = id
				attachment()
			}
		}
	}
	xhr.open('GET',"/archive/detail?fid="+id,true)
	xhr.send()
}


function deleteArticle(id){
	if(confirm("确认删除？如要恢复请联系管理员")){
		let xhr = new XMLHttpRequest()
		xhr.onreadystatechange=function(){
			if(xhr.readyState==4){
				if(xhr.status==200){
					let card = document.querySelector("[fid$='"+id+"']")
					card.parentNode.removeChild(card)
				}
			}
		}
		xhr.open('POST',"/delete/article?fid="+id,true)
		xhr.send()
	}
}

function buildCard(article){
	let card = document.createElement('div')
	card.className = "card"
	let title = document.createElement('div')
	title.className = "title"
	let snippet = document.createElement('div')
	snippet.className = "snippet"
	let post = document.createElement('div')
	post.className = "post"
	let hidden = document.createElement('button')
	hidden.className = "delete"
	title.innerHTML = article.title
	snippet.innerHTML = article.snippet
	post.innerHTML = timeFormat(article.post)
	card.setAttribute("fid",article.id)
	card.appendChild(hidden)
	card.appendChild(title)
	card.appendChild(snippet)
	card.appendChild(post)
	hidden.onclick = function (event){
		event.stopPropagation()
		deleteArticle(article.id)
	}
	card.onclick = function (){
		resetCardStyle()
		this.classList.add("focus")
		openArticle(article.id)
	}
	return card
}


function updateCard(card,article){
	let title = document.getElementsByClassName('title')[0]
	let snippet = document.getElementsByClassName('snippet')[0]
	let post = document.getElementsByClassName('post')[0]
	title.innerHTML = article.title
	snippet.innerHTML = article.snippet
	post.innerHTML = timeFormat(article.post)
}



function fillInput(title,subtitle,type,article){
	titleInput.value = title
	subtitleInput.value = subtitle
	typeInput.value = type
	simpleMDE.value(article)
}

createButton.onclick = function(){
	resetCardStyle()
	if(fidPrepared == null){
		fillInput("","",1,"")
		createArticle(function(){
			fidWorking = fidPrepared
			attachment()
		})
	}
	else if(fidWorking == fidPrepared){
		if(titleInput.value!=""||subtitleInput.value!=""||simpleMDE.value()!=""){
			if(confirm("确认清空输入框？")){
				fillInput("","",1,"")
			}
		}
		attachment()
	}
	else{
		fidWorking = fidPrepared
		fillInput("","",1,"")
		attachment()
	}
}


submitButton.onclick =  function(){
	if(titleInput.value==""||subtitleInput.value==""||simpleMDE.value()=="")
		return

	let xhr = new XMLHttpRequest()
	let title = titleInput.value
	let subtitle = subtitleInput.value
	let type = typeInput.value
	let article = simpleMDE.value()
	let postData = "title="+title+"&subtitle="+subtitle+"&type="+type+"&article="+article

	xhr.onreadystatechange=function(){
		if(xhr.readyState==4){
			if(xhr.status==200){
				let jsonBack = JSON.parse(xhr.responseText)
				let card = document.querySelector("[fid$='"+jsonBack.id+"']")
				if(card == null){
					card = buildCard(jsonBack)
					feedGallery.insertBefore(card,feedGallery.firstChild)
					fidPrepared = null
				}
				else{
					updateCard(card,jsonBack)
				}
			}
		}
	}
	xhr.open('POST',"/upload/article?fid="+fidWorking,true)
	xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded"); 
	xhr.send(postData)
}


window.onload = function(){
	new Feed(feedGallery)
	simpleMDE = new SimpleMDE(simpleMDEConfig)
	createButton.click()
}