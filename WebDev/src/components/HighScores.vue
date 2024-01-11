<template>
    <v-toolbar style="position: absolute; top: 0px; left: 0px; height: 7%;">
        <!-- TODO buton go back -->
        <v-btn @click="back()">
            <v-icon>mdi-undo-variant</v-icon>
        </v-btn>
        <v-app-bar-title>{{ name }}</v-app-bar-title>
        <v-btn @click="playGame()">
            <v-icon>mdi-gamepad-variant</v-icon>
        </v-btn>
        <v-btn @click="logOut()">
            <v-icon>mdi-logout</v-icon>
        </v-btn>
    </v-toolbar>
    <table id="scores">
        <tr>
            <th>Username</th>
            <th>Score</th>
        </tr>
        <tr v-for="i in scores.length" :key="i">
            <td>{{ scores[i - 1].username }}</td>
            <td>{{ scores[i - 1].score }}</td>
        </tr>
    </table>

    <!-- <button @click="updateScores()">Add Score</button> -->
</template>

<script>
import axios from 'axios'
export default {
    name: 'HighScores',
    props: ['name', 'gameid','user', 'userid', 'state'],
    data() {
        return {
            scores: [],
            score: Math.floor(Math.random() * (100 - 50 + 1) + 50)
        }
    },
    mounted() {
        this.init()
    },
    methods: {
        async init() {
            const api = axios.create({
                baseURL: 'http://127.0.0.1:5000',
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                timeout: 10000
            })

            const response = await api.get('/getScoresByGameId/' + this.gameid)
            this.scores = response.data.result
        },
        back() {
            this.$emit("changeState", 1)
        },
        logOut() {
            this.$emit("changeState", 0)
        },
        playGame() {
            this.$emit("changeState", Number.parseFloat(this.state) - 0.5)
        },
        async updateScores() {
            this.score = Math.floor(Math.random() * (100 - 50 + 1) + 50)
            const formData = new FormData()
            formData.append('game', this.gameid)
            formData.append('user', this.userid)
            formData.append('score', this.score)

            var position = -1 // user does not exist
            for ( var i = 0; i < this.scores.length; i++) {
                if (this.userid == this.scores[i].user) {
                    if (this.score > this.scores[i].score) {
                        position = i
                    } else {
                        position = -2 // user exists but scores is too low
                    }
                    break
                }
            }
            
            if (position == -1) {
                // POST
                const response = await axios.post('http://127.0.0.1:5000/addScore',
                    formData,
                    {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                })

                this.scores.push({'game': this.gameid, 'user': this.userid, 'username': this.user})
                this.getScore(response.data.id, this.scores.length - 1)
            } else {
                if (position != -2) {
                    // PUT
                        formData.append('_id', this.scores[position]._id)
                        const response = await axios.put('http://127.0.0.1:5000/addScore',
                        formData,
                        {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    })
                    this.getScore(response.data.id, position)
                }
            }
        },

        async getScore(id, index) {
            const api = axios.create({
                baseURL: 'http://127.0.0.1:5000',
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                timeout: 10000
            })

            const response = await api.get('/getScoreById/' + id)
            this.scores[index]['score'] = response.data.result
        }
    }
}
</script>

<style scoped>
#scores {
    width: 100%;
    border-collapse: collapse;
    position: absolute;
    right: 0px;
    left: 0px;
    top: 10%;
}

#scores td, #scores th {
    border: 1px solid #183b8f;
    padding: 8px;
    text-align: center;
}

#scores tr:nth-child(even) {
    background-color: #4287f5;
    color: white;
}

#scores tr:nth-child(odd) {
    color: #4287f5;
}

#scores tr:hover {
    background-color: #183b8f;
}

#scores th {
    background-color: #2f58ba;
    color: white;
}

</style>