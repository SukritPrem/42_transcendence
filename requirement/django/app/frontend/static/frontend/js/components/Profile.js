import { addNavigate, fetchJson, getUserAvatar, getUserName } from "./utils.js";

export class Profile extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template();
	}

	template = () => {
		return `
			<link rel="stylesheet" href="https://unicons.iconscout.com/release/v3.0.6/css/line.css">
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
			<link rel="stylesheet" href="${window.location.origin}/static/frontend/js/components/profile.css">
			
			<div id="container">
					<div id="profile-photo-big">
						<!--img id="avatar" src="${window.location.origin+"/user-media/avatars/default.png"}" alt="Profile Photo"
						onerror="this.onerror=null; this.src='${window.location.origin+"/user-media/avatars/default.png"}';"-->
						<img id="avatar" src="${window.location.origin+getUserAvatar()}" alt="Profile Photo"
						onerror="this.onerror=null; this.src='${window.location.origin+"/user-media/avatars/default.png"}';">
					</div>
				<a id="profile-name">
					<h4 id="username">${getUserName()}</h4>
				</a>
				<div id="side-bar">
					<div class="menu-item link-target" id="accountManagementLink" data-url="account-management" data-title="Baby cadet acount management">
						<span><i class="uil uil-user"></i></span>
						<h3>Account</h3>
					</div>
					<div class="menu-item link-target" id="notificationLink" data-url="notification" data-title="Baby cadet notification">
						<span><i class="uil uil-bell"></i></span>
						<h3>Notifications</h3>
					</div>
					<a class="menu-item link-target" id="statisticLink" data-url="statistic" data-title="Baby cadet statistic">
						<span><i class="uil uil-chart-bar"></i></span>
						<h3>Statistic</h3>
					</a>
					<a class="menu-item link-target" id="matchHistoryLink" data-url="match-history" data-title="Baby cadet match history">
						<span><i class="uil uil-file-alt"></i></span>
						<h3>Match History</h3>
					</a>
					<a class="menu-item link-target" id="blockedListLink" data-url="blocked-list" data-title="Baby cadet blocked list">
						<span><i class="uil uil-envelope-block"></i></span>
						<h3>Blocked List</h3>
					</a>
					<a class="menu-item" id="logOut">
						<span><i class="uil uil-signout"></i></span>
						<h3>Log Out</h3>
					</a>
				</div>
				<div id="offline-pong">
					<span><i class="uil uil-question-circle"></i></span>
					<div id="content">
						<h3 class="d-flex d-md-none d-xl-flex">Need Practice?</h3>
						<small>Play OFFLINE with friend!</small>
					</div>
					<button class="btn">Play OFFLINE</button>
				</div>
			</div>
		`;
	};

	logOut = async() => {
		const result = await fetchJson("logOut", "POST", `${window.location.origin}/api/auth/logout`)
		if (result) window.location.replace(window.location.origin)
	}

	connectedCallback() {		
		this.shadowRoot.querySelector("#logOut").addEventListener("click", this.logOut)

		// JavaScript to handle navigation and content loading
		document.addEventListener('DOMContentLoaded', () => {
			const parent = this.parentNode.parentNode
			const mainFrame = parent.getElementById("mainFrame")

			// Attach click event listener to navigation items
			this.shadowRoot.querySelectorAll('.link-target').forEach(item => addNavigate(item, mainFrame));
		});
	}
}
