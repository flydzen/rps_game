<script>
import Game from "@/components/Game/Game.vue";
import MyHeader from "@/components/Header/MyHeader.vue";
import LeaderBoard from "@/components/LeaderBoard/LeaderBoard.vue";

export default {
    components: {LeaderBoard, MyHeader, Game},
    data() {
        return {
            inGame: false, // SET TO TRUE TO DEBUG GAME WINDOW
            // user: {login: 'Anon', token: 'token'}, // ENABLE WHEN DEBUG
            user: null,
        }
    },
    methods: {
        onLogin(user) {
            this.user = user
        }
    }
}
</script>

<template>
    <MyHeader v-model:in-game="inGame" :user="user" @update:user="onLogin"/>
    <div id="content">
        <Game v-if="inGame" :user="user" @close-game="inGame"/>
        <LeaderBoard v-else :user="user"/>
    </div>
</template>

<style scoped>

#content {
    flex-grow: 1;
    width: 100%;
    margin: 0;
    padding: 0;
}
</style>
