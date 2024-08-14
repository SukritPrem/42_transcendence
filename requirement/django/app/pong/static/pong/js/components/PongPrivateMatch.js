import { getPongPublic, getUserName } from "/static/frontend/js/components/utils.js"

export class PongPrivateMatch extends HTMLElement {
	constructor() {
		super()
		this.attachShadow({mode: 'open'})
		this.shadowRoot.innerHTML = this.template()
	}

	template = () => {
		return `
			<p>PongPrivateMatch</p>
			<div id="waitRoom"></div>
		`
	}

	templatePlayers = (players) => {
		return players.map((player, index) => {
			return `
				<pong-player-component data-index="${index}" 
					data-name="${player.name}"
					data-avatar="${player.avatar}"
					data-status="${player.status}">
				</pong-player-component>
			`
		}).join("")
	}

	btnClick = (e) => {
		e.preventDefault()
		const index = e.target.dataset.index
		// const player = this.data.
		const {inviter, invited} = this.data
		const player = index === '0' ? inviter : invited
		player.status = player.status === 'wait' ? 'ready' : 'wait'
		// console.log (index, player.name)
		const pongPublic = getPongPublic()
		pongPublic.socket.send(JSON.stringify(this.data))
	}

	/** expect action = [update, beginpong] */
	update = (data) => {
		this.data = data
		// console.log("from PongPrivateMatch:")
		// console.log(this.data)
		if (this.data.action == 'update') {
			const players = [this.data.inviter, this.data.invited]
			this.shadowRoot.getElementById("waitRoom").innerHTML = this.templatePlayers(players)
			const player = this.shadowRoot.querySelector(`[data-name=${getUserName()}]`)
			const btn = player.shadowRoot.querySelector("button")
			btn.disabled = false
			btn.addEventListener("click", this.btnClick)
		} else {
			this.remove()
		}
	}

	connectedCallback() {

	}

	disconnectedCallback() {
		if (this.data.action == 'update'){
			this.data.action = 'quit'
			const pongPublic = getPongPublic()
			pongPublic.socket.send(JSON.stringify(this.data))
		}
	}
}