import { getUserAvatar } from "./Utils.js";
export class AccountManagment extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template();
	}

	template = () => {
		return `
			<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
			<link rel="stylesheet" href="${window.location.origin}/static/frontend/js/components/AccountManagment.css">
			
			<div class="bg-white overflow-auto custom-bg">
				<div id="header" class="fw-bold">
					<p>Account Managment</p>
				</div>
				<div id="topic" class="fw-bold">
					<p>Profile</p>
				</div>
				<div id="content" class="d-flex align-items-center justify-content-center">
					<div id="avatarCon" class="d-flex position-relative">
						<img id="profileImg" src="${window.location.origin+getUserAvatar()}" alt="Profile Photo"  class="position-absolute top-0 start-0 w-100 h-100"
							onerror="this.onerror=null; this.src='${window.location.origin+"/user-media/avatars/default.png"}';">
					</div>
					<div class="ms-0">
						<button class="d-flex align-items-center justify-content-center gap-2 border-0">Upload Image</button>
					</div>
				<div>
			</div>
		`;
	};

	connectedCallback() {

	}

	disconnectedCallback() {
		// console.log("delete Account Managment components");
	}
}

