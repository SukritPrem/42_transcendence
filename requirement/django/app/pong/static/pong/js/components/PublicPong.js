import { getMainFrame, getUserName } from "/static/frontend/js/components/Utils.js";

export class PublicPong extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template();
		this.username = getUserName()
		this.mainFrame = getMainFrame()
		this.tourBoardcast = this.shadowRoot.querySelector("toutnament-broadcast-component")
	}

	template = () => {
		return `
			<link rel="stylesheet" href="${window.location.origin}/static/pong/js/components/PublicPong.css">
			<toutnament-broadcast-component id="tourBoardcast"></toutnament-broadcast-component>
		`;
	};

	// publicUpdatePlayers = (data) => {
	// 	const tour = this.shadowRoot.querySelector("toutnament-broadcast-component")
	// 	tour.publicUpdatePlayers(Object.keys(data.players).length)
	// }

	setupWebsocket = () => {
		this.socket = new WebSocket(`${window.location.origin}/ws/pong/public`)

		this.socket.addEventListener("message", (ws)=>{
			const {type, data} = JSON.parse(ws.data)
			
			/** debug */
			// console.log({type, data})

			this.data = data

			if (type == "pong_private_message") {
				if (data.type == "private") {
					if (data.action == "error") {
						alert(data.message)
					}
				}
				else{
					// console.log(data)
					if (data.type == "tournament" && data.action == "update") {
						this.tourBoardcast.update()
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
						this.mainFrame.innerHTML = ""
					}
					else if (data.action == 'update') {
						let pongPrivateMatch = this.mainFrame.querySelector("#pongPrivateMatch")
						if (!pongPrivateMatch) {
							this.mainFrame.innerHTML = '<pong-private-match-component id="pongPrivateMatch"></pong-private-match-component>'
							pongPrivateMatch = this.mainFrame.querySelector("#pongPrivateMatch")
						}
						pongPrivateMatch.update(data)
					}
					else if (data.action == 'beginpong') {
						const pongPrivateMatch = this.mainFrame.querySelector("#pongPrivateMatch")
						pongPrivateMatch.update(data)
						console.log("beginpong")
						this.mainFrame.innerHTML = `
							<pong-component id="pongComponent" 
								data-player1="${data.game_data.player_one.name}" 
								data-player2="${data.game_data.player_two.name}">
							</pong-component>`
						data.action = 'playpong'
						this.socket.send(JSON.stringify(data))
					}
					else if (data.action == 'playpong') {
						const pongComponent = this.mainFrame.querySelector("#pongComponent")
						pongComponent.draw(data)
					}
					else if (data.action == 'finish') {
						const pongComponent = this.mainFrame.querySelector("#pongComponent")
						pongComponent.remove()
					}
					else {
						console.log(data)
					}
				}
				else if(data.type == 'tournament'){
					if (data.action == 'update') {
						const players = this.data.players
						// console.log(players)
						let isJoinBtn = true
						for (const player of players) {
							if (player.name == getUserName()) {
								// console.log("I am in tournament")
								let pongTourMatch = this.mainFrame.querySelector("#pongTourMatch")
								if (!pongTourMatch) {
									this.mainFrame.innerHTML = '<pong-tour-match-component id="pongTourMatch"></pong-tour-match-component>'
									pongTourMatch = this.mainFrame.querySelector("#pongTourMatch")
								}
								pongTourMatch.update()
								isJoinBtn = false
							}
						}
						this.tourBoardcast.update(isJoinBtn)
					}
					else if (data.action == 'waitmatch') {
						// const players = Object.values(data.players)
						this.tourBoardcast.update()
						for (const player of data.players) {
							if (player.name == getUserName()) {
								let pongTourMatch = this.mainFrame.querySelector("#waitMatch")
								if (!pongTourMatch) {
									this.mainFrame.innerHTML = '<wait-match-component id="waitMatch"></wait-match-component>'
									pongTourMatch = this.mainFrame.querySelector("#waitMatch")
								}
							}
						}
					}
					else if (data.action == 'beginpong') {
						console.log("beginpong")
						console.log(data)
						this.mainFrame.innerHTML = `
							<pong-component id="pongComponent" 
								data-player1="${data.game_datas[data.match_index].player_one.name}" 
								data-player2="${data.game_datas[data.match_index].player_two.name}">
							</pong-component>`
						data.action = 'playpong'
						this.socket.send(JSON.stringify(data))
					}
					else if (data.action == 'playpong') {
						const pongComponent = this.mainFrame.querySelector("#pongComponent")
						pongComponent.draw(data)
					}
					else if (data.action == 'finish') {
						console.log("game finish should remove pong component")
						// const pongComponent = this.mainFrame.querySelector("#pongComponent")
						// pongComponent.remove()
						this.mainFrame.innerHTML = ""
					}
					else {
						console.log(data)
					}
				}
				else {
					console.log(data)
				}
			}
		})
	}

	connectedCallback() {
		this.setupWebsocket()
		// console.log("tournament was connected")
	}

	disconnectedCallback() {
		this.socket.close()
	}
}
