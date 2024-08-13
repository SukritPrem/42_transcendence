import { getUserAvatar, getUserName } from "./utils.js"

export class DashBoardPage extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template()
	}

	template = () => {
		return `
			<link rel="stylesheet" href="https://unicons.iconscout.com/release/v4.0.8/css/line.css">
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
			<link rel="stylesheet" href="${window.location.origin}/static/frontend/js/components/DashBoardPage.css">
				
			<div id="nav" class="d-flex justify-content-between align-items-center w-100 position-relative ps-3 pe-3 bg-default">
				<div class="d-flex align-items-center">
					<div id="navMenu" class="rounded-0 align-items-center justify-content-center d-flex d-xl-none me-3">
						<i class="uil uil-bars fs-4 medium-gray"></i>
					</div>
					<div id="navLogo" class="d-none d-xl-flex align-items-center">
						<i class="uil uil-window-grid dark-text fs-4"></i>
						<p class="mb-0 ms-2 fw-bold fs-6 dark-text">DASHBOARD</p>
					</div>
				</div>
				<div id="navProfile" class="d-flex align-items-center">
					<div id="navProfileName" class="me-2 fw-bold fs-7 medium-gray ">
						${getUserName()}
					</div>
					<div id="navProfileAvatar">
						<img src="${window.location.origin + getUserAvatar()}" 
							alt="Profile Photo" id="profileImg"
							class="rounded"
							onerror="this.onerror=null; this.src='${window.location.origin+"/user-media/avatars/default.png"}';">
					</div>
				</div>
			</div>

			<div id="body" class="d-flex bg-default">
				<profile-component id="profileComponent" class="body-left"></profile-component>
				<div id="bodyMiddle" class="bg-default">
					<public-pong-component id="pongPublic"></public-pong-component>
					<div id="mainFrame">
						<!--notification-component></notification-component-->
					</div>

				</div>
				<div id="bodyRight" class="bg-default">
					<friends-component id="friendsComponent"></friends-component>
					<live-chat-component id="liveChatComponent"></live-chat-component>
				</div>
			</div>

			<div id="footer" class="d-flex align-items-center justify-content-center container-fluid position-fixed bottom-0 start-0">
				<p class="medium-gray fs-8 m-0">
					@ 2024, Made with 
					<i class="uil uil-heart-alt"></i> 
					by 
					<span class="primary-color fw-bold">42 Baby Cadet</span>
				</p>
			</div>
		`;
	}

	toggleProfileVisibility = () => {
		const profile = this.shadowRoot.getElementById('profileComponent');
		if (profile) {
			profile.style.display = profile.style.display === 'block' ? 'none' : 'block';
		}
	}

	connectedCallback() {
		const menuIcon = this.shadowRoot.getElementById('navMenu');
		if (menuIcon) {
			menuIcon.addEventListener('click', this.toggleProfileVisibility);
		}
	}
}