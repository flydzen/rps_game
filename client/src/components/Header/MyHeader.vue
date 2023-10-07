<script>
import UserBlock from "@/components/Header/UserBlock.vue";

export default {
    name: "MyHeader",
    components: {UserBlock},
    props: {
        inGame: {
            type: Boolean,
            required: true,
        },
        user: {
            type: String,
            required: false,
        }
    },
    methods: {
        onSignIn(user) {
            this.$emit('update:user', user)
        },
        onStart() {
            if (this.user == null) {
                alert("Зарегестрируйтесь")
            } else {
                this.$emit('update:in-game', true)
            }
        }
    },
    emits: ['update:user', 'update:in-game']
}
</script>

<template>
    <header>
        <div class="header-item left-item" id="header-title">
            <p>Камень ножницы бумага</p>
        </div>
        <div class="header-item center-item">
            <button id="leave-game-button" v-if="inGame" @click="this.$emit('update:in-game', false)">
                Покинуть игру
            </button>
            <button id="start-game-button" v-else @click="onStart">
                Начать игру
            </button>
        </div>
        <UserBlock class="header-item right-item" :user="user" @update:user="onSignIn"/>
    </header>
</template>

<style scoped>
header {
    padding: 14px;
    background-color: #242424;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
}

button {
    display: inline-block;
    padding: 10px 20px;
    background-color: #263468;
    color: white;
    height: 70px;
    width: 200px;
    text-decoration: none;
    border: none;
    border-radius: 5px;
    font-size: 20pt;
}

button:hover {
    background-color: #0056b3;
}

.header-item {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}

.header-item > * {
    align-self: center;
}

.left-item {
    text-align: left;
    font-size: 20pt;
}

.center-item {
    text-align: center;
}

.right-item {
    text-align: right;
}
</style>