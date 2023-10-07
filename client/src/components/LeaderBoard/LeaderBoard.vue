<script>
import LeaderBoardItem from "@/components/LeaderBoard/LeaderBoardItem.vue";
import axios from "axios";
import {server_http_url} from "@/config";

export default {
    name: "LeaderBoard",
    components: {LeaderBoardItem},
    props: {
        user: {
            type: String,
            required: false,
        },
    },
    methods: {
        async getLeaderboard() {
            await axios.get(
                server_http_url + '/leaderboard?limit=100'
            ).then(
                response => this.items = response.data
            );
        },
        async getUserScore() {
            await axios.get(
                server_http_url + '/leaderboard/user/' + this.user
            ).then(
                response => this.userScore = response.data
            );
        },
    },
    data() {
        return {
            items: [],
            userScore: null,
        };
    },
    created() {
        this.getLeaderboard();
    },
    watch: {
        user: {
            handler(value) {
                if (this.user !== null)
                    this.getUserScore()
            },
            immediate: true,
        }
    }
}
</script>

<template>
    <div class="container">
        <h1>Leaderboard</h1>
        <div id="table-container">
            <table>
                <thead>
                <LeaderBoardItem id="item-header" :item=
                    "{
                        position: '№',
                        login: 'login',
                        victories: 'victories',
                        losses: 'losses',
                    }"
                />
                </thead>
                <tbody>
                <LeaderBoardItem id="row-self" v-if="userScore !== null" :item="userScore"/>
                <LeaderBoardItem v-for="item in items" :item="item"/>
                </tbody>
            </table>
        </div>
    </div>
</template>

<style scoped>
.container {
    width: 60%;
    min-width: 500px;
    margin: 0 auto;
    padding: 20px;
}

#table-container {
    overflow-y: auto;
    max-height: 70vh;
    border-radius: 10px;
}

#table-container thead #item-header > ::v-deep(th) {
    position: sticky;
    top: -10px;
}

#row-self > ::v-deep(th) {
    background-color: #3F3C49;
}

table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 10px;
    color: #d9d9d9;
}

thead {
    height: 60px;
    font-size: 16pt;
    color: #4c63bb;
}

#item-header > ::v-deep(th) {
    background-color: #242424;
}

::-webkit-scrollbar {
    width: 10px;
}

/* Track */
::-webkit-scrollbar-track {
    background: #545454;
    border-radius: 0 10px 10px 0;

}

/* Handle */
::-webkit-scrollbar-thumb {
    background: #263468;
    border-radius: 0 10px 10px 0;
}

/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
    background: #0056b3;
}

</style>