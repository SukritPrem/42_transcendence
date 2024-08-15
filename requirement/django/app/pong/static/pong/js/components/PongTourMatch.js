import { getPongPublic, getUserName } from "/static/frontend/js/components/Utils.js"

export class PongTourMatch extends HTMLElement {
	constructor () {
		super()
		this.attachShadow({mode: 'open'})
		this.shadowRoot.innerHTML = this.template()
		this.waitRoom = this.shadowRoot.getElementById("waitRoom")
		this.pongPublic = getPongPublic()
	}

	template = () => {
		return `
			<link rel="stylesheet" href="https://unicons.iconscout.com/release/v4.0.8/css/line.css">
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
			<link rel="stylesheet" href="${window.location.origin}/static/pong/js/components/PongTourMatch.css">
			
			<div class="bg-white overflow-auto custom-bg">
				<div id="header" class="fw-bold">
					<p>Pong Tournament</p>
				</div>
				<div class="border-line"></div>
				<div id="waitRoom"></div>
			</div>
		`
	}

	templatePlayers = (players) => {
		return players.map((player, index) => {
			return `
				<pong-player-component id="${player.name}" data-index="${index}" 
					data-name="${player.nickname}"
					data-avatar="${player.avatar}"
					data-status="${player.status}">
				</pong-player-component>
			`
		}).join("")
	}

	btnClick = (e) => {
		e.preventDefault()
		for (const player of this.pongPublic.data.players) {
			if (player.name == getUserName()){
				player.status = player.status === 'wait' ? 'ready' : 'wait'
				this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
			}
		}
	}

	update = () => {
		this.waitRoom.innerHTML = this.templatePlayers(this.pongPublic.data.players)
		const player = this.shadowRoot.getElementById(getUserName())
		const btn = player.shadowRoot.querySelector("button")
		btn.disabled = false
		btn.addEventListener("click", this.btnClick)
	}

	disconnectedCallback() {
		if (this.pongPublic.data.action == 'update'){
			this.pongPublic.data.action = 'quit'
			this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
		}
	}
}