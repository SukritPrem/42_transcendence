import { getCSRFToken, getUserAvatar, getUserId } from "./Utils.js";
export class AccountManagment extends HTMLElement {
	constructor() {
		super();
		this.attachShadow({ mode: "open" });
		this.shadowRoot.innerHTML = this.template();
	  this.uploadAvatar =	this.uploadAvatar.bind(this)
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
						<img id="profileImg" src="${getUserAvatar()}" 
							alt="Profile Photo"  class="position-absolute top-0 start-0 w-100 h-100"
							role="button"
							onerror="this.onerror=null; this.src='${window.location.origin+"/user-media/avatars/default.png"}';">
					</div>
					<form id="formAvatar">
						<input type="text" class="d-none" name="user_id" value="${getUserId()}">
						<input id="avatarInput" class="input-img d-none"
							type="file" value=""
							name="avatar" accept="image/*">
						<div class="ms-0">
							<button type="submit"
								class="d-flex align-items-center justify-content-center gap-2 border-0" 
								id="uploadBtn">Upload Image
							</button>
						</div>
					</form>
				<div>
			</div>
		`;
	};

	async uploadAvatar(e) {
		e.preventDefault()
		try {
			const avatarInput = this.shadowRoot.getElementById('avatarInput')
			if (!avatarInput.value) {
				alert('Click your avatar to choose new one before upload.')
				return
			}

			const csrfToken = getCSRFToken();
			if (!csrfToken) {
				throw new Error("CSRF token not found");
			}

			const form = e.target
			const formData = new FormData(form)

			const response = await fetch(`/api/users/update_avatar`, {
				method: 'POST',
				credentials: "same-origin",
				headers: {
					"X-CSRFToken": csrfToken
				},
				body: formData,
			});

			const result = await response.json();
			if (response.status == 201){
				alert("Avatar changed!!")
				console.log(result)
			}
			else
				throw new Error(`${response.status} ${response.statusText} ${result.error}`)

		}
		catch (error) {
			console.error('Error uploadAvatar:', error);
		}
	}

	connectedCallback() {
		const profileImg = this.shadowRoot.getElementById("profileImg")
		const avatarInput = this.shadowRoot.getElementById('avatarInput')
		const formAvatar = this.shadowRoot.getElementById('formAvatar')
		profileImg.addEventListener('click', ()=>{
			avatarInput.click()
		})
		avatarInput.addEventListener('change', ()=>{
			// console.log(avatarInput.value)
			if (avatarInput.value)
				profileImg.src = URL.createObjectURL(avatarInput.files[0]);
			else
				profileImg.src = getUserAvatar()
		})
		formAvatar.addEventListener('submit', this.uploadAvatar)
	}

	disconnectedCallback() {
		// console.log("delete Account Managment components");
	}
}

