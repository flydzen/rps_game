<script>
import axios from "axios";
import {server_http_url} from "@/config";

export default {
    name: "AuthorizedBlock",
    props: {
        user: {
            type: String,
            required: false,
        },
    },
    methods: {
        logOut() {
            axios.delete(server_http_url + '/users/token')
            this.$emit('update:user', null);
        }
    },
    emits: ['update:user']
}
</script>

<template>
    <div id="authorized-root">
        <p>{{ user }}</p>
        <button id="logout-btn" @click="logOut">Log out</button>
    </div>
</template>

<style scoped>
#authorized-root {
    display: flex;
    flex-direction: row;
    align-items: center;
}

#authorized-root > * {
    margin: 20px;
}

#logout-btn {
    border: none;
    background-color: #682626;
    margin-left: 0;
    border-radius: 5px;
    height: 30px;
}

#logout-btn:hover {
    background-color: #b30000;
}
</style>