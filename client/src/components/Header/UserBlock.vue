<script>
import AuthorizedBlock from "@/components/Header/AuthorizedBlock.vue";
import UnauthorizedBlock from "@/components/Header/UnauthorizedBlock.vue";
import Cookies from "js-cookie";
import * as jose from "jose";
import {JWKS, server_http_url} from "@/config";
import axios from "axios";

export default {
    name: "UserBlock",
    components: {UnauthorizedBlock, AuthorizedBlock},
    props: {
        user: {
            type: Object,
            required: false,
        },
    },
    methods: {
        userChanged(user) {
            this.$emit('update:user', user)
        }
    },
    beforeCreate() {
        axios.post(
            server_http_url + '/users/token'
        ).then(
            (userData) => this.$emit('update:user', userData.data.login)
        ).catch(
            () => axios.delete(server_http_url + '/users/token')
        );
    },
    emit: ['update:user']
}
</script>

<template>
    <div id="user-block">
        <AuthorizedBlock v-if="user != null" :user="user" @update:user="userChanged"/>
        <UnauthorizedBlock v-else @update:user="userChanged"/>
    </div>
</template>

<style scoped>
#user-block > div {
    box-shadow: 0 0 30px 4px rgba(0, 0, 0, 0.62);
    border-radius: 10px;
    padding: 5px;
    margin: 5px;
}
</style>