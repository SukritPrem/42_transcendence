import { getMainFrame, getUserName } from "/static/frontend/js/components/utils.js";

export class PublicPong extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template();
		this.username = getUserName()
	}

	template = () => {
		return `
			<link rel="stylesheet" href="${window.location.origin}/static/pong/js/components/PublicPong.css">
			<tournament-upcomming-component></tournament-upcomming-component>
		`;
	};

	setupWebsocket = () => {
		this.socket = new WebSocket(`${window.location.origin}/ws/pong/public`)

		this.socket.addEventListener("message", (ws)=>{
			const {type, data} = JSON.parse(ws.data)
			// console.log({type, data})

			if (type == "pong_private_message") {
				if (data.type == "private") {
					if (data.action == "error") {
						alert(data.message)
					}
				}
			}
			else if (type == "pong_public_message") {
				if (data.type == "private") {
					if (data.action == "inviter"){
						if (this.username == data.invited.name) {
							console.log(`${data.inviter.name} invited you to play game`)
							data.action = "invited"
							this.socket.send(JSON.stringify(data))
						}
					}
					else if (data.action == 'quit') {
						console.log(`recieve quit message`)
						const mainFrame = getMainFrame()
						mainFrame.innerHTML = ""
					}
					else if (data.action == 'update') {
						const mainFrame = getMainFrame()
						let pongPrivateMatch = mainFrame.querySelector("#pongPrivateMatch")
						if (!pongPrivateMatch) {
							mainFrame.innerHTML = '<pong-private-match-component id="pongPrivateMatch"></pong-private-match-component>'
							pongPrivateMatch = mainFrame.querySelector("#pongPrivateMatch")
						}
						pongPrivateMatch.update(data)
					}
					else if (data.action == 'beginpong') {
						const mainFrame = getMainFrame()
						const pongPrivateMatch = mainFrame.querySelector("#pongPrivateMatch")
						pongPrivateMatch.update(data)
						console.log("beginpong")
						mainFrame.innerHTML = `<pong-component id="pongComponent" data-player1="${data.game_data.player_one.name}" data-player2="${data.game_data.player_two.name}"></pong-component>`
						
						// console.log(data)

						data.action = 'playpong'
						// console.log(data)
						this.socket.send(JSON.stringify(data))
						// const pongComponent = mainFrame.querySelector("#pongComponent")
						// pongComponent.draw(data.game_data)
					}
					else if (data.action == 'playpong') {
						const mainFrame = getMainFrame()
						const pongComponent = mainFrame.querySelector("#pongComponent")
						pongComponent.draw(data)
					}
					else if (data.action == 'finish') {
						const mainFrame = getMainFrame()
						const pongComponent = mainFrame.querySelector("#pongComponent")
						pongComponent.remove()
					}
					else {
						console.log(data)
					}
				}
			}
		})
	}

	connectedCallback() {
		this.setupWebsocket()
		console.log("tournament was connected")
	}

	disconnectedCallback() {
		this.socket.close()
	}
}
