<script>
import axios from "axios";
import {server_http_url} from "@/config";

export default {
    name: "UnauthorizedBlock",
    methods: {
        async signUp() {
            let authData = {
                login: this.loginField,
                password: this.passwordField,
            };
            await axios.post(
                server_http_url + '/users/signup', authData
            ).then(
                () => this.userUpdated(authData.login)
            ).catch(
                (e) => {
                    if (e.response.status === 409)
                        alert("This login is already in use")
                    else
                        alert('Error ' + e.response.status)
                }
            );
        },
        async signIn() {
            let authData = {
                login: this.loginField,
                password: this.passwordField,
            };
            await axios.post(
                server_http_url + '/users/signin', authData
            ).then(
                () => this.userUpdated(authData.login)
            ).catch(
                (e) => {
                    if (e.response.status === 403)
                        alert("Wrong login or password")
                    else
                        alert("Error " + e.response.status)
                }
            );
        },
        userUpdated(user) {
            this.$emit('update:user', user)
        }
    },
    data() {
        return {
            loginField: '',
            passwordField: '',
        }
    },
    emits: ['update:user']
}
</script>

<template>
    <div id="unauthorized-root">
        <div id="user-inputs">
            <input id="login-input" type="text" v-model.trim="loginField" placeholder="login"/>
            <input id="password-input" type="password" v-model="passwordField" placeholder="password"/>
        </div>
        <div id="user-btns">
            <button id="signup-btn" @click="signUp">Sign up</button>
            <button id="login-btn" @click="signIn">Log in</button>
        </div>
    </div>
</template>

<style scoped>
#unauthorized-root {
    display: flex;
}

#unauthorized-root > div {
    display: flex;
    flex-direction: column;
}

#user-btns > button {
}

input {
    height: 30px;
    width: 200px;
    padding: 0 5px;
    border: 0;
    border-radius: 6px;
    margin: 5px;
}

button {
    height: 30px;
    width: 90px;
    margin: 5px;
    border: none;
    color: white;
    font-size: 12pt;
}

#signup-btn {
    background-color: #263468;
}

#login-btn {
    background-color: #266844;
}
</style>