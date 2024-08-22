import { getUserName, getPongPublic } from "/static/frontend/js/components/Utils.js"

export class Pong extends HTMLElement {
	constructor () {
		super()
		// this.user = document.querySelector("[name=context-user]").value || null
		this.user = getUserName()
		this.attachShadow({mode: 'open'})
		this.shadowRoot.innerHTML = this.template()
		this.keyDownHandler = this.keyDownHandler.bind(this)
		this.pongPublic = getPongPublic()
	}

	template() {
		return `
			<link rel="stylesheet" href="${window.location.origin}/static/pong/js/components/Pong.css" />
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
			
			<div style="text-align: center">Pong Game</div>
			<div class="canvas-container border border-danger">
				<canvas id="canvas"></canvas>
			</div>
		`
	}

	drawBall(canvas, ctx, data, isPortrait){
		let x, y, r
		if (isPortrait){		
			x = canvas.width - (this.scaleX * data.ball.y)
			// x = this.scaleX * data.ball_y
			y = this.scaleY * data.ball.x;
			
			if (this.user == data.player_one.name) {
				y = canvas.height - y
				x = canvas.width - x
			}

		} else {
			x = this.scaleX * data.ball.x;
			y = this.scaleY * data.ball.y

			//invert
			// x = canvas.width - (this.scaleX * data.ball_x);
			// y = canvas.height - (this.scaleY * data.ball_y);
		}
		r = this.scaleY * data.ball_radius

		ctx.beginPath()
		ctx.arc( x, y, r, 0, Math.PI * 2, true)
		ctx.closePath()
		ctx.fill();
	}

	drawPlayer(canvas, ctx, data, isPortrait){
		const paddingWidth = 10
		const paddingRadius = this.scaleY * data.player_radius

		if (isPortrait) {

			// let upper, lower
			let lower = this.scaleX * data.player_one.y - paddingRadius
			let upper = this.scaleX * data.player_two.y - paddingRadius
			// let upper = canvas.width - (this.scaleX * data.player_two_y) - paddingRadius
			if (this.user == data.player_two.name) {
				lower = canvas.width - (this.scaleX * data.player_two.y) - paddingRadius
				// upper = canvas.width - (this.scaleX * data.player_one_y - paddingRadius)
				upper = canvas.width - (this.scaleX * data.player_one.y)- paddingRadius
			}
			//owner
			ctx.fillRect(
				// this.scaleX * data.player_one_y - paddingRadius, 
				lower,
				canvas.height - paddingWidth,
				paddingRadius * 2,
				paddingWidth
				)

			//anothor
			ctx.fillRect(
				// this.scaleX * data.player_two_y - paddingRadius,
				upper,
				0,
				paddingRadius * 2,
				paddingWidth
			)
		}
		else {
			// player1
			ctx.fillRect(
				0,
				this.scaleY * data.player_one.y - paddingRadius, 
				paddingWidth,
				paddingRadius * 2,
				)

			// player2
			ctx.fillRect(
				canvas.width - paddingWidth,
				this.scaleY * data.player_two.y - paddingRadius,
				paddingWidth,
				paddingRadius * 2,
			)
		}
	}

	setUpScale(canvas, data, isPortrait){
		if (isPortrait) {
			this.scaleX = canvas.width / data.table.height;
			this.scaleY = canvas.height / data.table.width;
		} else {
			this.scaleX = canvas.width / data.table.width;
			this.scaleY = canvas.height / data.table.height;
		}
	}

	draw(datas) {
		this.datas = datas
		// console.log(datas)
		// let data
		// if (datas.type == 'private') {
		// 	data = datas.game_data
		// }
		// else if (datas.type == 'tournament') {
		const data = datas.game_datas[datas.match_index]
			// console.log(datas)
			// console.log(data)
		// }
		const canvas = this.shadowRoot.getElementById("canvas")
		canvas.width = canvas.offsetWidth
		canvas.height = canvas.offsetHeight
		const ctx = canvas.getContext("2d")
		ctx.clearRect(0, 0, canvas.width, canvas.height)

		const isPortrait = canvas.width < canvas.height;

		this.setUpScale(canvas, data, isPortrait)
		// console.log(`{${x}: ${y}}`)
		this.drawBall(canvas, ctx, data, isPortrait)
		this.drawPlayer(canvas, ctx, data, isPortrait)
	}

	sendMoveMent(direction){
		const data = {
			user: this.user,
			type: "move",
			move: direction
		}
		this.socket.send(JSON.stringify(data))
	}

	keyDownHandler(e){
		// console.log(e.key)
		switch(e.key){
			case "a":
			case "w":
			case "ArrowLeft":
			case "ArrowUp":
				this.sendMoveMent("left");
				break;
			case "s":
			case "d":
			case "ArrowRight":
			case "ArrowDown":
				this.sendMoveMent("right"); 
				break;
			default: break
		}
	}

	sendMoveMent(direction){
		this.datas.action = 'sendkey'
		this.datas.direction = direction
		this.pongPublic.socket.send(JSON.stringify(this.datas))
	}

	connectedCallback(){
		if(this.user == this.dataset.player1 || this.user == this.dataset.player2)
			document.addEventListener('keydown', this.keyDownHandler)
	}

	disconnectedCallback() {
		if(this.user == this.dataset.player1 || this.user == this.dataset.player2)
				document.removeEventListener('keydown', this.keyDownHandler)
		
		// if (this.pongPublic.data.type == 'private') {
		// 	this.pongPublic.data.action = 'quit'
		// 	// const pongPublic = getPongPublic()
		// 	this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
		// }
		// else if (this.pongPublic.data.type == 'tournament') {
			if (this.pongPublic.data.action != 'finish') {
				console.log(this.pongPublic.data)
				this.pongPublic.data.action = 'quit'
			}
			this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
			console.log(this.pongPublic.data)
		// }
	}
}