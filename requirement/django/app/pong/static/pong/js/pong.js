import { PublicPong } from "./components/PublicPong.js";
import { TourBroadcast } from "./components/TourBroadcast.js"
import { PongPrivateMatch } from "./components/PongPrivateMatch.js"
import { PongTourMatch } from "./components/PongTourMatch.js";
import { Pong } from "./components/Pong.js"
import { PongPlayer } from "./components/PongPlayer.js"
import { WaitMatch } from "./components/WaitMatch.js"

customElements.define('public-pong-component', PublicPong)
customElements.define("toutnament-broadcast-component", TourBroadcast)
customElements.define("pong-private-match-component", PongPrivateMatch)
customElements.define("pong-tour-match-component", PongTourMatch)
customElements.define("pong-component", Pong)
customElements.define("pong-player-component", PongPlayer)
customElements.define("wait-match-component", WaitMatch)