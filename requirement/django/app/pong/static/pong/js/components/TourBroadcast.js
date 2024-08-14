import { getPongPublic } from "/static/frontend/js/components/utils.js"

export class TourBroadcast extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template();
		this.pongPublic = getPongPublic()
		this.boardCast = this.shadowRoot.getElementById("tourBroadcast")
	}

	template = () => {
	return `
			<link rel="stylesheet" href="${window.location.origin}/static/pong/js/components/TourBroadcast.css">
			<link rel="stylesheet" href="https://unicons.iconscout.com/release/v3.0.6/css/line.css">
			
			<div id="tourBroadcast"></div>
		`;
	}

	joinTourTemplate = (number) => {
		return `
			<span>
				<i class="uil uil-check-circle"></i>
			</span>
			<div id="content">
				<h4>TOURNAMENT is upcoming ...</h4>
				<small>registered member (<span id="amountPlayer" style="display: inline;">${number}</span>/4)</small>
			</div>
			<button class="btn" id="joinBtn">JOIN TOURNAMENT</button>
		`
	}

	update = () => {
		if (this.pongPublic.data.action == 'update') {
			this.boardCast.innerHTML = this.joinTourTemplate(this.pongPublic.data.players.length)
			const joinBtn = this.shadowRoot.getElementById('joinBtn');
			joinBtn.addEventListener('click', this.joinTour);
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
