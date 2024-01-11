<template>
    <v-toolbar style="position: absolute; top: 0px; left: 0px; height: 7%;">
        <v-btn @click="search()">
            <v-icon>mdi-magnify</v-icon>
        </v-btn>
        <v-text-field single-line hide-details id="search" @input="search()"></v-text-field>
        <v-btn @click="logOut()">
            <v-icon>mdi-logout</v-icon>
        </v-btn>
    </v-toolbar>
    <v-container style="position: absolute; left: 50px; right: 50px; background-color: azure; top: 7%">
        <v-row>
            <v-col v-for="i in count" :key="i" cols="3" :id="'element' + i">
                <v-card class="mx-auto" max-width="400" heoght="400px" @click="selectGame(i)">
                    <v-img :src="'http://127.0.0.1:5000/getImageById/' +  games[i - 1].image" height="200px" cover></v-img>
                    <v-card-title>{{ games[i - 1].title }}</v-card-title>
                    <v-card-text>{{ games[i - 1].description }}</v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
    import axios from 'axios'
    export default {
        name: "Menu",
        data () {
            return {
                games: [],
                count: 0
            }
        },
        mounted () {
            this.init()
        },
        methods: {
            async init () {
                const api = axios.create({
                    baseURL: 'http://127.0.0.1:5000',
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    },
                    timeout: 10000
                })

                const response = await api.get('/getGames')
                this.games = response.data.result
                this.count = this.games.length
            },

            search() {
                for (var i = 0; i < this.count; i++){
                    if (this.games[i].title.toLowerCase().includes(document.getElementById("search").value.toLowerCase())) {
                        document.getElementById('element' + (i + 1)).style.display = "block"
                    } else {
                        document.getElementById('element' + (i + 1)).style.display = "none"
                    }
                }
            },

            selectGame(pos) {
                this.$emit("changeState", pos + 1)
                this.$emit("selectedGame", this.games[pos - 1].title)
                this.$emit("selectedGameId", this.games[pos - 1]._id)
            },

            logOut() {
                this.$emit("changeState", 0)
            }
        }
    }
</script>

<style scoped>
</style>