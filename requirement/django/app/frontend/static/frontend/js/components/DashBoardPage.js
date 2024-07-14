import { getCSRFToken } from "./utils.js"

export class DashBoardPage extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.userData = {}
	}

	/*fetchUser = async() => {
		try {
			const csrfToken = getCSRFToken();
			if (!csrfToken) {
				throw new Error("CSRF token not found");
			}

			const owner_id = localStorage.get("owner_id")

			const response = await fetch("api/users/:user_id/:owner_id/profile", {
				method: 'GET',
				credentials: "same-origin",
				headers: {
					"X-CSRFToken": csrfToken,
					"Content-Type": "application/json"
				},
				body: JSON.stringify(data),
			});
  
		if (!response.ok) {
			throw new Error(`Fetch error: ${response.status} ${response.statusText}`);
		}

		const json = await response.json()
			// console.log(json)
			localStorage.setItem("owner_id", json.owner_id);
		} catch (error) {
			console.error('Error fetching friends:', error);
		}
	}*/

	template = () => {
		return `
			<link rel="stylesheet" href="https://unicons.iconscout.com/release/v4.0.8/css/line.css">
			<link rel="stylesheet" href="${window.location.origin}/static/frontend/js/components/DashBoardPage.css">
				
			<div id="navBar">
				<div id="container">
					<div id="menu">
						<i class="uil uil-bars"></i>
					</div>
					<div id="logo">
						<i class="uil uil-window-grid"></i>
						<h2>DASHBOARD</h2>
					</div>
					<div id="profile">
						<div id="profile-name">
							<p><b>Prem</b></p>
						</div>
						<div id="profile-photo">
							<!--img src="../images/profile-1.jpg" alt="Profile Photo"-->
						</div>
					</div>
				</div>
			</div>

			<div id="div-content">
				<profile-component id="proFile"></profile-component>
				<div id="div-middle">
					<tour-na-ment></tour-na-ment>
					<notifi-cation></notifi-cation>
				</div>
				<div id="div-right">
					<friends-block></friends-block>
					<live-chat></live-chat>
				</div>
			</div>

			<div id="footer">
				<p>
					@ 2024, Made with 
					<i class="uil uil-heart-alt"></i> 
					by 
					<span>42 Baby Cadet</span>
				</p>
			</div>
		`;
	}

	toggleProfileVisibility = () => {
		const profile = this.shadowRoot.getElementById('proFile');
		if (profile) {
			profile.style.display = profile.style.display === 'none' ? 'block' : 'none';
		}
	}

	connectedCallback() {
		this.shadowRoot.innerHTML = this.template();
		const menuIcon = this.shadowRoot.getElementById('menu');
		if (menuIcon) {
			menuIcon.addEventListener('click', this.toggleProfileVisibility);
		}
	}
}