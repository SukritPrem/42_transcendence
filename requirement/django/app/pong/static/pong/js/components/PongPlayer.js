export class PongPlayer extends HTMLElement{
	constructor() {
		super()
		this.attachShadow({mode: 'open'})
		this.shadowRoot.innerHTML = this.template()
	}

	template = () => {
		return `
			<div class="player" data-index="${this.dataset.index}">
				<div class="player-name">${this.dataset.name}</div>
				<div>
					<img class="player-avatar" src="${this.dataset.avatar}"/>
				</div>
				<div>
					<button data-name="${this.dataset.name}" data-index="${this.dataset.index}" 
						class="player-status" disabled>${this.dataset.status}</button>
				</div>
			</div>
		`
	}
}