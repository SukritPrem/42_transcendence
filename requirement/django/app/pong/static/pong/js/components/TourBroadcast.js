import { getPongPublic, getSessionID, getUserName } from "/static/frontend/js/components/Utils.js"

export class TourBroadcast extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template();
		this.pongPublic = getPongPublic()
		this.boardCast = this.shadowRoot.getElementById("tourBroadcast")
		this.privateInvite = false
		this.sessionID = getSessionID()
		this.username = getUserName()
	}

	template = () => {
	return `
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
			<link rel="stylesheet" href="https://unicons.iconscout.com/release/v3.0.6/css/line.css">
			<link rel="stylesheet" href="${window.location.origin}/static/pong/js/components/TourBroadcast.css">
			
			<div id="tourBroadcast" class="d-flex flex-column flex-md-row align-items-center"></div>
		`;
	}

	joinTourTemplate = (number) => {
		return `
			<span id="icon" class="d-none d-lg-flex align-items-center">
				<i class="uil uil-check-circle position-relative d-inline-flex justify-content-center align-items-center m-0"></i>
			</span>
			<div id="content" class="d-flex flex-column justify-content-center me-auto">
				<h4 class="m-0 text-white fw-bold">TOURNAMENT is upcoming ...</h4>
				<small>
					registered member (
					<span id="amountPlayer">${number}</span>
					/ 4 )
				</small>
			</div>
			<button class="btn btn-light" id="joinBtn">JOIN TOURNAMENT</button>
		`
	}

	waitmatchTemplate = () => {
		const game_data = this.pongPublic.data.game_datas[this.pongPublic.data.match_index]
		return `
			<div id="content">
				<h4 class="m-0 text-white fw-bold">${game_data.player_one.nickname} VS ${game_data.player_two.nickname}</h4>
			</div>
		`
	}

	privateInviteUpdate = () => {
		const inviter = this.pongPublic.data.players[0]
		const invited = this.pongPublic.data.players[1]
		if (this.username == inviter.name){
			this.privateInvite = true
			this.boardCast.innerHTML = `
				<div id="content">
					<h4 class="m-0 text-white fw-bold">You invite game with ${invited.name}, wait for accept</h4>
				</div>
			`
		}
		else if (this.username == invited.name){
			this.privateInvite = true
			this.boardCast.innerHTML = `
				<div id="content">
					<h4 class="m-0 text-white fw-bold">${inviter.name} invite you to play pong</h4>
					<button class="btn btn-info" id="acceptBtn">ACCEPT</button>
					<button class="btn btn-danger" id="rejectBtn">REJECT</button>
				</div>
			`
			this.shadowRoot.getElementById('acceptBtn').addEventListener('click', ()=>{
				this.pongPublic.data.action = 'invited'
				this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
			})
			this.shadowRoot.getElementById('rejectBtn').addEventListener('click', ()=>{
				this.pongPublic.data.action = 'reject'
				this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
			})
		}
	}

	/** privateInvited */
	privateInvited = () => {
		const inviter = this.pongPublic.data.players[0]
		const invited = this.pongPublic.data.players[1]

		if (this.username == inviter.name || this.username == invited.name) {
			this.privateInvite = false
			this.pongPublic.data.action = 'request_tour_message'
			this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
			/** make sure only one session can send request update */
			if (this.sessionID == inviter.session_id) {
				this.pongPublic.data.action = 'update'
				this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
			}
		}
	}

	/** only inviter can handle message */
	// privateReject = () => {
	// 	const inviter = this.pongPublic.data.players[0]
	// 	const invited = this.pongPublic.data.players[1]

	// 	if (this.username == inviter.name || this.username == invited.name) {
	// 		this.privateInvite = false
	// 		this.pongPublic.data.action = 'request_tour_message'
	// 		this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
	// 	}
	// }

	update = (isJoinBtn=true) => {
		if (this.privateInvite) return
		if (this.pongPublic.data.action == 'update') {
			this.boardCast.innerHTML = this.joinTourTemplate(this.pongPublic.data.players.length)
			const joinBtn = this.shadowRoot.getElementById('joinBtn');
			if (isJoinBtn) {
				joinBtn.style.display = ''
				joinBtn.addEventListener('click', this.joinTour);
			} else {
				joinBtn.style.display = 'None'
			}
		}
		else if (this.pongPublic.data.action == "waitmatch") {
			this.boardCast.innerHTML = this.waitmatchTemplate()
		}
	}

	joinTour = () => {
		const nickname = prompt("nickname: ")
		if (nickname != null) {
			const data = {
				"type": "tournament",
				"action": "join",
				"nickname": nickname
			}
			this.pongPublic.socket.send(JSON.stringify(data))
		}
	}

	connectedCallback() {
	}
}
