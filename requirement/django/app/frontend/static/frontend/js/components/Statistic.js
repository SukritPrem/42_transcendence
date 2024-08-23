import { fetchJson } from "./Utils.js";

export class Statistic extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template();
	}

	template = () => {
		return `
			<link rel="stylesheet" href="https://unicons.iconscout.com/release/v3.0.6/css/line.css">
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
			<link rel="stylesheet" href="${window.location.origin}/static/frontend/js/components/Statistic.css">
			
			<div class="bg-white overflow-auto custom-bg">
				<div id="header" class="fw-bold">
					<p>Statistic</p>
				</div>
				<div class="w-100 d-flex flex-column align-items-center justify-content-center gap-3">
					<div class="list-item">
						<i class="uil uil-globe"></i>
						<p class="text">MATCH</p>
						<p id="match" class="fw-bold amount">11</p>
					</div>
					<div class="list-item">
						<i class="uil uil-arrow-growth"></i>
						<p class="text">WIN</p>
						<p id="win" class="fw-bold amount">5</p>
					</div>
					<div class="list-item">
						<i class="uil uil-chart-down"></i>
						<p class="text">LOSE</p>
						<p id="lose" class="fw-bold amount">2</p>
					</div>
					<div class="list-item">
						<i class="uil uil-chart-down"></i>
						<p class="text">DRAW</p>
						<p id="draw" class="fw-bold amount">2</p>
					</div>
				</div>
			</div>
		`;
	};

	async fetchStatistic() {
		const result = await fetchJson('fetchStatistic', 'GET', `${window.location.origin}/pong/statictis`)
		if (result) {
			// console.log(result)
			this.shadowRoot.getElementById('match').innerText = result.match
			this.shadowRoot.getElementById('win').innerText = result.win
			this.shadowRoot.getElementById('lose').innerText = result.lose
			this.shadowRoot.getElementById('draw').innerText = result.draw
		}
	}

	connectedCallback() {
		this.fetchStatistic()
	}

	disconnectedCallback() {
		// console.log("delete")
	}
}
