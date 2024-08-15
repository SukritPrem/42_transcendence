import { getPongPublic } from "/static/frontend/js/components/Utils.js"

export class WaitMatch extends HTMLElement {
	constructor() {
		super()
		this.attachShadow({mode: 'open'})
		this.pongPublic = getPongPublic()
		this.shadowRoot.innerHTML = this.template()
	}

	template = () => {
		return `<div>WaitMatch</div>`
	}

	connectedCallback() {
		// setTimeout(()=>{
		// 	this.pongPublic.data.action = 'nextmatch'
		// 	this.pongPublic.socket.send(this.pongPublic.data)
		// }, 3000)
	}

	disconnectedCallback() {
		console.log("disconnectedCallback")
		console.log(this.pongPublic.data)
		console.log(this.pongPublic.data.action)
		if (this.pongPublic.data.action == 'waitmatch') {
			console.log("send quit to server")
			this.pongPublic.data.action = 'quit'
			this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
		}
	}
}