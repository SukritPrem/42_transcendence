import { getPongPublic } from "/static/frontend/js/components/utils.js"

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
}