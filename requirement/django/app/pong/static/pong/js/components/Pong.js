import { getUserName, getPongPublic } from "/static/frontend/js/components/Utils.js"

export class PongBase extends HTMLElement {
	constructor () {
		super()
		this.user = getUserName()
		this.attachShadow({mode: 'open'})
		this.shadowRoot.innerHTML = this.template()
		// this.keyDownHandler = this.keyDownHandler.bind(this)
		// this.pongPublic = getPongPublic()
	}

	template() {
		return `
			<link rel="stylesheet" href="${window.location.origin}/static/pong/js/components/Pong.css" />
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
			
			<!--div style="text-align: center">Pong Game</div-->
			<!--div class="canvas-container border border-danger"-->
			<div class="canvas-container">
				<canvas id="canvas"></canvas>
			</div>
		`
	}

	drawBall(canvas, ctx, data, isPortrait){
		let x, y, r
		if (isPortrait){		
			x = canvas.width - (this.scaleX * data.ball.y)
			y = this.scaleY * data.ball.x;
			if (this.user == data.player_one.name) {
				y = canvas.height - y
				x = canvas.width - x
			}
		} else {
			x = this.scaleX * data.ball.x;
			y = this.scaleY * data.ball.y
		}
		r = this.scaleY * data.ball_radius

		ctx.save()
		ctx.fillStyle = '#F8F9FA'
		ctx.beginPath()
		ctx.arc( x, y, r, 0, Math.PI * 2, true)
		ctx.closePath()
		ctx.fill();
		ctx.restore()
	}

	drawPlayer(canvas, ctx, data, isPortrait){
		const fontSize = 24
		const fontMargin = 10
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
			ctx.save()
			ctx.fillStyle = "#E53E3E"
			ctx.fillRect(
				// this.scaleX * data.player_one_y - paddingRadius, 
				lower,
				canvas.height - paddingWidth,
				paddingRadius * 2,
				paddingWidth
				)

			ctx.font = `${fontSize}px serif`
			ctx.fillText (
				data.player_one.score,
				fontMargin,
				(canvas.height / 2 ) + fontSize,
				)
			
			//anothor
			ctx.fillStyle = "#2D3748"
			ctx.fillRect(
				// this.scaleX * data.player_two_y - paddingRadius,
				upper,
				0,
				paddingRadius * 2,
				paddingWidth
			)

			// ctx.font = `${fontSize}px serif`
			ctx.fillText (
				data.player_two.score,
				fontMargin,
				(canvas.height / 2 ) - fontMargin,
				)
			ctx.restore()
		}
		else {
			// player1
			ctx.save()
			ctx.fillStyle = "#E53E3E"
			ctx.fillRect(
				0,
				this.scaleY * data.player_one.y - paddingRadius, 
				paddingWidth,
				paddingRadius * 2,
				)
			
			ctx.font = `${fontSize}px serif`
			ctx.fillText (
				data.player_one.score,
				(canvas.width / 2 ) - (fontSize + fontMargin),
				fontSize + fontMargin
				)

			// player2
			ctx.fillStyle = "#2D3748"
			ctx.fillRect(
				canvas.width - paddingWidth,
				this.scaleY * data.player_two.y - paddingRadius,
				paddingWidth,
				paddingRadius * 2,
			)

			ctx.fillText (
				data.player_two.score,
				(canvas.width / 2 ) + fontMargin,
				fontSize + fontMargin
			)
			ctx.restore()
		}
	}

	drawScreen(canvas, ctx){
		ctx.save()
		ctx.fillStyle = '#4FD1C5'
		ctx.fillRect(
			0,
			0,
			canvas.width,
			canvas.height,
		)
		ctx.restore()
	}

	drawHalf(canvas, ctx, isPortrait){
		ctx.save()
		ctx.fillStyle = "#F8F9FA"
		if (isPortrait) {
			ctx.fillRect(
				0,
				(canvas.height / 2) - 1,
				canvas.width,
				2
			)
		} else {
			ctx.fillRect(
				(canvas.width / 2) - 1,
				0, 
				2,
				canvas.height)
		}
		ctx.restore()
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
		const data = datas.game_datas[datas.match_index]
		const canvas = this.shadowRoot.getElementById("canvas")
		canvas.width = canvas.offsetWidth
		canvas.height = canvas.offsetHeight
		const ctx = canvas.getContext("2d")
		ctx.clearRect(0, 0, canvas.width, canvas.height)
		const isPortrait = canvas.width < canvas.height;
		this.setUpScale(canvas, data, isPortrait)

		this.drawScreen(canvas, ctx)
		this.drawHalf(canvas, ctx, isPortrait)
		this.drawBall(canvas, ctx, data, isPortrait)
		this.drawPlayer(canvas, ctx, data, isPortrait)
	}
}

export class Pong extends PongBase {
	constructor(){
		super()
		this.keyDownHandler = this.keyDownHandler.bind(this)
		this.pongPublic = getPongPublic()
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
		if (this.pongPublic.data.action != 'finish') {
			console.log(this.pongPublic.data)
			this.pongPublic.data.action = 'quit'
		}
		this.pongPublic.socket.send(JSON.stringify(this.pongPublic.data))
	}
}