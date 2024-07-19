const { Builder, By } = require('selenium-webdriver');
const { describe, it, after, before } = require('mocha');
// const assert = require("assert");
const configs = require("./configs")
const testTitle = require("./testTitle")
const testSignUp = require("./testSignUp")
const testLogin = require("./testLogin")
const testMainFrame = require("./testMainFrame")
const testFriendRequest = require("./testFriendRequest")
const testFriendDecline = require("./testFriendDecline")
const testFriendAccept = require("./testFriendAccept")
const testFriendProfile = require("./testFriendProfile")

describe('Test Babycadet begin', function() {
	this.timeout(60000);
	let driver;

	before(async () => {
		driver = await new Builder().forBrowser('chrome').build();
		await driver.get(configs.url);
	});

	it('should open and title is Baby cadet first page', async ()=>testTitle(driver));

	it('should signup', async () => testSignUp(driver));

	it('should login', async () => testLogin(driver));

	it('test main frame', async () => testMainFrame(driver));

	it('test friend request', async () => testFriendRequest(driver));

	it('test friend decline', async () => testFriendDecline(driver));

	it('test friend accept', async () => testFriendAccept(driver));

	it('test friend profile', async () => testFriendProfile(driver));	

	after(async () => {
		await driver.quit();
	});
});
