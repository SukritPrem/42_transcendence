// want props "data-chatroom, data-username, data-userid"
// to find chatroom name in database

import { fetchJson, getUserName } from "/static/frontend/js/components/utils.js";

export class LiveChat extends HTMLElement {
	static observedAttributes = ["data-chatroom"];
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template();
	}

	template = () => {
		return `
			<link rel="stylesheet" href="${window.location.origin}/static/chat/js/components/LiveChat.css">
			
			<div id="liveChat">
				<div id="header">
					<div>
						<h4>Live Chat</h4>
						<div id="avatar">
							
						</div>
					</div>
					<div id="chatroom"></div>
				</div>
			</div>
		`;
	}

	chatroomTemplate = (messages) => {
		return `
			<div id="chatMessages">
			${messages.map(mes=>{
				return this.messageTemplate(mes.fields.author, mes.fields.body)
			}).join("")}
			</div>
			<form id="messageForm">
				<input id="inputMessage" type="text" >
				<button id="sendMessageBtn" type="submit">Send</button>
			</form>
		`
	}

	/*
	* this.dataset.userid : other user
	*/
	messageTemplate = (author, message) => {
		if (author == this.dataset.userid) {
			return `
				<div class="other-user-message"">
					<div class="message">${message}</div>
					<div class="username">@${this.dataset.username}</div>
				</div>
			`
		}
		else {
			return `
				<div class="owner-message">
					<div class="message">${message}</div>
					<div class="username">@${getUserName()}</div>
				</div>
			`
		}
	}

	connectedCallback() {
	}

	scrollToBottom = () => {
		const container = this.shadowRoot.getElementById('chatMessages')
		container.scrollTop = container.scrollHeight
	}

	sendMessage = async(e) => {
		e.preventDefault()
		const inputMessage = this.shadowRoot.getElementById("inputMessage")
		// console.log(inputMessage.value)

		const dashBoardComponent = document.getElementById("dashBoardComponent")
		const friendsComponent = dashBoardComponent.shadowRoot.getElementById("friendsComponent")
		const friend = friendsComponent.shadowRoot.querySelector(`#${this.dataset.username}`)
		// console.log(friend)

		const message = {"type": "message", "body": inputMessage.value}
		friend.socket.send(JSON.stringify(message))
		inputMessage.value = ""
	}

	fetchChatRoom = async (chatroom) => {
		const result = await fetchJson("fetchChatRoom", "GET", 
			`${window.location.origin}/chat/private/${chatroom}`)
		if (result) {
			// console.log(result)
			const messages = JSON.parse(result)
			const chatroom = this.shadowRoot.getElementById("chatroom")
			chatroom.innerHTML = this.chatroomTemplate(messages)
			this.scrollToBottom()
			this.shadowRoot.getElementById("messageForm")
				.addEventListener('submit', this.sendMessage)
			const avatar = document.createElement("img")
			avatar.setAttribute("src", `${window.location.origin}${this.dataset.avatar}`)
			this.shadowRoot.getElementById("avatar").innerHTML = avatar.outerHTML
		}
	}

	updateChatRoom = (obj) => {
		const chatMessages = this.shadowRoot.getElementById("chatMessages")
		if (obj.type == "message_handler")
			chatMessages.innerHTML += this.messageTemplate(obj.message.author, obj.message.body)
		if (obj.type == "invite_private_pong_handler")
			console.log (obj)
		this.scrollToBottom()
	}

	attributeChangedCallback(name, oldValue, newValue) {
		// console.log(`Attribute ${name} has changed ${newValue}.`);
		//fetch old chat
		this.fetchChatRoom(newValue)
	}

	resetLiveChat = () => {
		this.shadowRoot.innerHTML = this.template()
	}
}
