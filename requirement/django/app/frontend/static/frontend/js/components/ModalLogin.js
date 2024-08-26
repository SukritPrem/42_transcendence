import { fetchJson, getCSRFToken } from "./Utils.js";

export class ModalLogin extends HTMLElement {

	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template()
	}

	template = () => {
		return `
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
			<link rel="stylesheet" href="./static/frontend/js/components/ModalLogin.css">

			<form id="signInForm">
				<p id="textWelcome" class="text-center fw-bold">Welcome Back</p>
				<p class="text-gray d-none d-sm-flex text-center fw-bold d-flex justify-content-center align-items-center">Enter your username and password to sign in</p>
				<div id="usernameCon" class="d-flex align-items-center justify-content-center">
					<label for="username">Username</label>
					<input class="input-css" type="text" 
						placeholder="Your username" id="username" 
						autocomplete="username"
						name="username" required>
				</div>
				<div id="passwordCon" class="d-flex align-items-center justify-content-center">
					<label for="password">Password</label>
					<input class="input-css" type="password" 
						placeholder="Your password" id="password" 
						autocomplete="current-password"
						name="password" required>
				</div>
				<button id="loginButton" class="btn container-fluid d-flex align-items-center justify-content-center" type="submit">SIGN IN</button>
			</form>
			</div>
			<div>
				<p class="text-gray text-center fw-bold">or</p>
			</div>
			<div id="signInWith">
				<p class="text-gray text-center fw-bold">Sign In with</p>
				<button id="btn42" class="btn container-fluid d-flex align-items-center justify-content-center">
					<img src="./static/frontend/images/42eco.png" alt="42 icon">
				</button>
			</div>
		`;
	}

	login = async(e)=>{
		e.preventDefault()
		const data = {
			username: this.shadowRoot.querySelector("#username").value,
			password: this.shadowRoot.querySelector("#password").value
		}
		const result = await fetchJson("login", "POST", "api/auth/login", data)
		// alert(JSON.stringify(result))
		if (result) {
			if(result.message === '2fa') {
				window.location.replace(window.location.origin + "/api/2fa-page")
			} else {
				window.location.replace(window.location.origin + "/dashboard")
			}
		}
		else {
			alert("something wrong try again")
			this.shadowRoot.querySelector("#username").value = ""
			this.shadowRoot.querySelector("#password").value = ""
		}
	}
	
	login42 = (e) => {
		e.preventDefault()
		window.location.replace(`${window.location.origin}/api/auth/login42`)	
	}

	connectedCallback(){
		this.shadowRoot.getElementById("signInForm").addEventListener('submit', this.login)
		this.shadowRoot.getElementById("btn42").addEventListener('click', this.login42)
	}

	disconnectedCallback(){
		console.log("ModalLogin was gone")
	}
}
