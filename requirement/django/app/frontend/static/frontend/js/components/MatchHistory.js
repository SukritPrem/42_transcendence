const Mock_hx = [
	{
		matchType: 'Tournament',
		date: '7 Jun 2024',
		opponentPlayer: 'Sarah',
		outcome: 'lose',
	},
	{
		matchType: '1 vs 1',
		date: '7 Jun 2024',
		opponentPlayer: 'Sarah',
		outcome: 'lose',
	},
	{
		matchType: '1 vs 1',
		date: '7 Jun 2024',
		opponentPlayer: 'Sarah',
		outcome: 'lose',
	},
	{
		matchType: 'Tournament',
		date: '7 Jun 2024',
		opponentPlayer: 'Sarah',
		outcome: 'lose',
	},
	{
		matchType: 'Tournament',
		date: '7 Jun 2024',
		opponentPlayer: 'Sarah',
		outcome: 'lose',
	},
	{
		matchType: 'Tournament',
		date: '7 Jun 2024',
		opponentPlayer: 'Sarah',
		outcome: 'lose',
	}
];

export class MatchHistory extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
	}

	template = () => {
		return `
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
			<link rel="stylesheet" href="${window.location.origin}/static/frontend/js/components/MatchHistory.css">
			
			<div class="bg-white overflow-auto custom-bg">
				<div id="header" class="fw-bold">
					<p>Match History</p>
				</div>
				<table>
					<thead>
						<tr>
							<th>Type</th> 
							<th>Date</th>
							<th>Opponent player</th>
							<th>Outcome</th>
						</tr>
					</thead>
					<tbody id="matchHistoryTableBody">
					</tbody>
				</table>
			</div>
		`;
	};

	connectedCallback() {
		this.shadowRoot.innerHTML = this.template();
		
		const tbody = this.shadowRoot.querySelector('table tbody');

		Mock_hx.forEach(mock => {
			const tr = document.createElement('tr');
			const trContent = `
				<td>${mock.matchType}</td>
				<td>${mock.date}</td>
				<td>${mock.opponentPlayer}</td>
				<td>${mock.outcome}</td>
			`;
			tr.innerHTML = trContent;
			tbody.appendChild(tr);
		});
	}

	disconnectedCallback() {
		console.log("delete match history components");
	}
}
