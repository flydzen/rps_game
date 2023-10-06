<script>
import LeaderBoardItem from "@/components/LeaderBoard/LeaderBoardItem.vue";
import axios from "axios";
import {server_http_url} from "@/config";

export default {
    name: "LeaderBoard",
    components: {LeaderBoardItem},
    methods: {
        async loadLeaders() {
            await axios.get(
                server_http_url + '/leaderboard'
            ).then(
                response => this.items = response.data
            );
        }
    },
    data() {
        return {
            items: []
        };
    },
    created() {
        this.loadLeaders();
    }
}
</script>

<template>
    <div class="container">
        <h1>Таблица лидеров</h1>
        <div id="table-container">
            <table>
                <thead>
                <tr>
                    <th>№</th>
                    <th>Login</th>
                    <th>Wins</th>
                    <th>Loses</th>
                </tr>
                </thead>
                <tbody>
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

#table-container thead th {
    position: sticky;
    top: -10px;
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

th, td {
    border: 2px solid #2e2e31;
    text-align: left;
    padding: 8px;
}

th {
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