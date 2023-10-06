<script>
import {Casts, Statuses} from "@/enums"
import PlayerBar from "@/components/Game/PlayerBar.vue";
import Timer from "@/components/Game/Timer.vue";
import VideoResult from "@/components/Game/VideoResult.vue";
import {server_ws_url} from "@/config";

export default {
  name: "Game",
  components: {VideoResult, Timer, PlayerBar},
  props: {
    user: {
      type: String,
      required: false,
    }
  },
  computed: {
    Casts() {
      return Casts
    },
    Statuses() {
      return Statuses
    }
  },
  data() {
    return {
      status: Statuses.WAITING_FOR_OPPONENT,
      myCast: Casts.NONE,
      opponent: null,
      opponentCast: Casts.NONE,
      websocket: null,
      isConnected: false,
      deadline: null,
      revengeRequested: false,
    }
  },
  methods: {
    connectWebSocket() {
      console.log("Creating game connection");
      this.websocket = new WebSocket(server_ws_url + '/game');

      this.websocket.addEventListener('open', () => {
        this.isConnected = true;
      });

      this.websocket.addEventListener('message', (event) => {
        console.log('Получено сообщение:', event.data);
        this.onMessage(JSON.parse(event.data));
      });

      this.websocket.addEventListener('close', () => {
        this.isConnected = false;
      });

      this.websocket.addEventListener('error', (error) => {
        console.error('Произошла ошибка WebSocket:', error);
        this.isConnected = false;
        this.closeGame();
        alert('Какая-то ошибка.');
      });
    },
    onMessage(message) {
      this.status = message.game_status;
      this.opponent = message.opponent_name;
      this.opponentCast = message.cast_opponent;
      this.myCast = message.cast_you;
      this.deadline = message.deadline;
      if (this.status === Statuses.IN_PROGRESS)
        this.revengeRequested = false;
    },
    sendJSON(json) {
      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        this.websocket.send(JSON.stringify(json));
      }
    },
    closeGame() {
      console.log("Close game")
      if (this.websocket) {
        console.log("Disconnecting")
        this.websocket.close();
      }
      this.$emit('close-game', false);
    },
    handleMove(cast) {
      console.log("Sent " + cast)
      this.sendJSON({
        cast: cast
      });
      this.myCast = cast;
    },
    hasOpponentLeft() {
      return this.status !== Statuses.WAITING_FOR_OPPONENT && this.opponent === null;
    },
    revengeShow() {
      if (this.hasOpponentLeft())
        return false
      return this.status === Statuses.LOSE || this.status === Statuses.WIN;
    },
    handleRevengeClick() {
      console.log("Revenge request");
      this.sendJSON( {
        revenge: true
      });
      this.revengeRequested = true;
    }
  },
  created() {
    this.connectWebSocket();
  },
  beforeDestroy() {
    console.log("before destoy")
    this.closeGame()
  },
  beforeUnmount() {
    console.log("before unmount")
    this.closeGame()
  }
}
</script>

<template>
  <div id="game-container">
    <PlayerBar
        :login="opponent"
        :selected="opponentCast"
        :disabled="true"
        :class="'block top'
          + (opponentCast===Casts.HIDDEN ? ' ready' : '')
          + (hasOpponentLeft() ? ' leave' : '')"
    />
    <div class="center">
      <div class="block left">2</div>
      <div class="block mid">
        <div id="middle-interaction">
          <p id="status">{{status}}</p>
          <button
              id="revenge-btn"
              :class="revengeRequested ? 'r-btn-requested' : ''"
              @click="handleRevengeClick"
              v-if="revengeShow()"
          >revenge</button>
        </div>
        <VideoResult :casts="[myCast, opponentCast]"/>
      </div>
      <Timer class="block right" :deadline="deadline"/>
    </div>
    <PlayerBar
        :login="user"
        :disabled="status!==Statuses.IN_PROGRESS"
        :class="'block bot'
          + (myCast!==Casts.NONE && status===Statuses.IN_PROGRESS ? ' ready' : '')
          + (isConnected ? '' : ' leave')"
        :selected="myCast"
        @on-select="handleMove"
    />
  </div>
</template>

<style scoped>
#middle-interaction {
  position: absolute;
  font-size: 32pt;
  display: flex;
  flex-direction: column;
  z-index: 1;
  align-items: center;
}

#revenge-btn {
  padding: 10px 20px;
  background-color: #3e3c3c;
  color: white;
  height: 70px;
  width: 160px;
  text-decoration: none;
  border-radius: 5px;
  box-shadow: 0 0 20px 4px rgba(0, 0, 0, 0.25);
  font-size: 20pt;
  transition-duration: 0.3s;
}

#revenge-btn:hover, #revenge-btn.r-btn-requested {
  background-color: #3f4177;
}

#game-container {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.center {
  display: flex;
  flex-grow: 1;
}

.block.mid {
  flex-grow: 1;
  background-color: #484748;
  margin: 20px;
}

.block {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-size: 20px;
  line-height: 20px;
  color: #ffffff;
  border-radius: 10px;
  border: 10px;
  background-color: #3E3C3C;
}

.top {
  border-radius: 0 0 30px 30px;
  box-shadow: 0 10px 8px -2px rgba(0, 0, 0, 0.25);
  transition-duration: 0.3s;
}

.top.ready {
  box-shadow: 0 10px 8px -2px greenyellow;
}

.top.leave {
  box-shadow: 0 10px 8px -2px darkred;
}

.bot {
  border-radius: 30px 30px 0 0;
  box-shadow: 0 -10px 8px -2px rgba(0, 0, 0, 0.25);
  transition-duration: 0.4s;
}

.bot.ready {
  box-shadow: 0 -10px 8px -2px greenyellow;
}

.bot.leave {
  box-shadow: 0 -10px 8px -2px darkred;
}

.left {
  border-radius: 0 30px 30px 0;
  height: 66%;
  width: 66px;
  align-self: center;
  box-shadow: 10px 0 8px -2px rgba(0, 0, 0, 0.25);
}

.right {
  border-radius: 30px 0 0 30px;
  height: 66px;
  width: 66px;
  align-self: center;
  box-shadow: -10px 0 8px -2px rgba(0, 0, 0, 0.25);
}

</style>