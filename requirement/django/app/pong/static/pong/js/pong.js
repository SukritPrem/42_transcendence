import { PublicPong } from "./components/PublicPong.js";
import { TournamentUpcoming } from "./components/TournamentUpcoming.js"
import { PongPrivateMatch } from "./components/PongPrivateMatch.js"
import { Pong } from "./components/Pong.js"

customElements.define('public-pong-component', PublicPong)
customElements.define("tournament-upcomming-component", TournamentUpcoming)
customElements.define("pong-private-match-component", PongPrivateMatch)
customElements.define("pong-component", Pong)