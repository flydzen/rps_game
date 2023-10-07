<script>
import {Casts} from "@/enums";

export default {
    name: "PlayerBar",
    computed: {
        Casts() {
            return Casts
        }
    },
    props: {
        login: {
            type: String,
            default: '?',
        },
        selected: {
            type: String,
            required: true,
        },
        disabled: {
            type: Boolean,
            default: false,
        }
    },
    methods: {
        getBtnClass(owner) {
            if (this.selected === owner)
                return 'cast-btn selected';
            return 'cast-btn';
        },
        processClick(cast) {
            this.$emit('on-select', cast);
        }
    },
    emits: ['on-select']
}
</script>

<template>
    <div class="player-bar">
        <div class="bar-item"></div>
        <div class="cast-btn-holder bar-item">
            <button :class="getBtnClass(Casts.ROCK)" :disabled="disabled" @click="() => processClick(Casts.ROCK)">
                <img src="@/assets/imgs/stone160.png" alt="Rock"/>
            </button>
            <button :class="getBtnClass(Casts.SCISSORS)" :disabled="disabled"
                    @click="() => processClick(Casts.SCISSORS)">
                <img src="@/assets/imgs/scissors160.png" alt="Scissors"/>
            </button>
            <button :class="getBtnClass(Casts.PAPER)" :disabled="disabled" @click="() => processClick(Casts.PAPER)">
                <img src="@/assets/imgs/paper160.png" alt="Paper"/>
            </button>
        </div>
        <div class="bar-item">
            <p>{{ login }}</p>
        </div>
    </div>
</template>

<style scoped>
.player-bar {
    width: 80%;
    height: 80px;
    margin: 0 auto;
    justify-content: space-evenly;
}

.cast-btn {
    height: 80px;
    width: 80px;
    background-color: #464646;
    border: none;
    color: white;
    transition-duration: 0.4s;
    padding: 0;
}

.cast-btn > img {
    height: 80px;
    width: 80px;
    transition-duration: 0.4s;
}

.cast-btn:hover, .cast-btn:hover > img {
    border-radius: 16px;
}

.cast-btn:disabled {
    background-color: #242424;
}

.cast-btn:hover:disabled, .cast-btn:hover:disabled > img {
    border-radius: 0;
}

.bar-item.cast-btn-holder {
    width: 320px;
    display: flex;
    justify-content: space-between;
}

.selected {
    box-shadow: 0 0 0 4px greenyellow;
}

.bar-item {
    width: 150px;
    word-wrap: break-word;
    text-align: center;
}
</style>