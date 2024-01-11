<template>
    <v-toolbar style="position: absolute; top: 0px; left: 0px; height: 7%;">
        <!-- TODO buton go back -->
        <v-btn @click="back()">
            <v-icon>mdi-undo-variant</v-icon>
        </v-btn>
        <v-app-bar-title>{{ name }}</v-app-bar-title>
        <v-btn @click="highScore()">
            HIGH SCORES
        </v-btn>
        <v-btn @click="logOut()">
            <v-icon>mdi-logout</v-icon>
        </v-btn>
    </v-toolbar>
    
</template>

<script>
import * as THREE from 'three'
import { CSS2DRenderer, CSS2DObject} from 'three/examples/jsm/renderers/CSS2DRenderer'
import axios from 'axios'
export default {
    name: 'Pong',
    props: ['name', 'gameid','user', 'userid', 'state'],
    mounted () {
        this.init_scores()
        this.init()
    },
    data () {
        return {
            keyboard: {},
            backgroundSprites: [],
            level: 1,
            time: 0,
            auxTime: 0,
            pressTime: 0,
            playerPoints: 0,
            enemyPoints: 0,
            enemyDirection: 1,
            ballDirectionX: -1,
            ballDirectionY: 1,
            levels: [{"rounds": 5, "speed": 1},
                        {"rounds": 5, "speed": 1.1},
                        {"rounds": 3, "speed": 1.2},
                        {"rounds": 3, "speed": 1.3},
                        {"rounds": 1, "speed": 1.4}],
            ballY: Math.random() * (3 - (-3)) + (-3),
            won: 0,
            score: 0,
            updatedScore: 0, 
            paused :0,
            scores: []
        }
    },
    methods: {
        back() {
            this.$emit("changeState", 1)
            document.getElementById('canvas').remove()
            document.getElementById('timerLabel').remove()
        },
        logOut() {
            this.$emit("changeState", 0)
            document.getElementById('canvas').remove()
            document.getElementById('timerLabel').remove()
        },
        highScore() {
            this.$emit("changeState", Number.parseFloat(this.state) + 0.5)
            document.getElementById('canvas').remove()
            document.getElementById('timerLabel').remove()
        },
        init () {
            // Event listeners
            window.addEventListener('keydown', this.keyDown)
            window.addEventListener('keyup', this.keyUp)
            window.addEventListener('resize', this.resize)

            // Create Scene
            this.scene = new THREE.Scene()

            // Get Clock
            this.clock = new THREE.Clock()

            // Create Camera
            this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
            
            this.camera.position.y = 0
            this.camera.position.z = 5
            this.camera.lookAt(new THREE.Vector3(0, 0, 0))

            // Background
            var textureLoader = new THREE.TextureLoader()
            this.backgroundSprites.push(textureLoader.load('/pong/1.png'))
            this.backgroundSprites.push(textureLoader.load('/pong/2.png'))
            this.backgroundSprites.push(textureLoader.load('/pong/3.png'))
            this.backgroundSprites.push(textureLoader.load('/pong/4.png'))
            this.backgroundSprites.push(textureLoader.load('/pong/5.png'))
            this.backgroundMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(17, 10, 100, 100),
                new THREE.MeshBasicMaterial({
                    map: this.backgroundSprites[this.level - 1]
                })
            )
            this.scene.add(this.backgroundMesh)

            // Net
            var netTexture = textureLoader.load("/pong/net.png")
            this.netMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.1, 5.25, 100, 100),
                new THREE.MeshBasicMaterial({
                    map: netTexture,
                    transparent: true
                })
            )
            this.netMesh.position.z = 1
            this.netMesh.position.y = -0.25
            this.scene.add(this.netMesh)

            // Player
            var barTexture = textureLoader.load("/pong/bar.png")
            this.playerMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.2, 1.5, 100, 100),
                new THREE.MeshBasicMaterial({
                    map: barTexture,
                    transparent: true
                })
            )
            this.playerMesh.position.x = -7
            this.scene.add(this.playerMesh)

            // Enemy
            this.enemyMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.2, 1.5, 100, 100),
                new THREE.MeshBasicMaterial({
                    map: barTexture,
                    transparent: true
                })
            )
            this.enemyMesh.position.x = 7
            this.scene.add(this.enemyMesh)

            // Ball
            var ballTexture = textureLoader.load("/pong/ball.png")
            this.ballMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.5, 0.5, 100, 100),
                new THREE.MeshBasicMaterial({
                    map: ballTexture,
                    transparent: true
                })
            )
            this.scene.add(this.ballMesh)

            // Text Renderer
            this.timerDiv = document.createElement('div')
            this.timerDiv.id = 'timerDiv'
            this.timerDiv.textContent = 'Time: 0'
            this.timerDiv.style.backgroundColor = "transparent"
            this.timerDiv.style.fontSize = '30px'
            this.timerDiv.style.color = "white"
            const timerLabel = new CSS2DObject(this.timerDiv)
            timerLabel.position.set(-5, 0, 0)
            this.scene.add(timerLabel)
            timerLabel.layers.set(0)

            this.pointsDiv = document.createElement('div')
            this.pointsDiv.id = 'pointsDiv'
            this.pointsDiv.textContent = '0 : 0'
            this.pointsDiv.style.backgroundColor = 'transparent'
            this.pointsDiv.style.fontSize =  '30px'
            this.pointsDiv.style.color = "white"
            const pointsLabel = new CSS2DObject(this.pointsDiv)
            pointsLabel.position.set(0, 0, 0)
            this.scene.add(pointsLabel)
            pointsLabel.layers.set(0)

            this.levelDiv = document.createElement('div')
            this.levelDiv.id = 'levelDiv'
            this.levelDiv.textContent = 'Level 1'
            this.levelDiv.style.backgroundColor = 'transparent'
            this.levelDiv.style.fontSize =  '30px'
            this.levelDiv.style.color = "white"
            const levelLabel = new CSS2DObject(this.levelDiv)
            levelLabel.position.set(5, 0, 0)
            this.scene.add(levelLabel)
            levelLabel.layers.set(0)

            this.labelRenderer = new CSS2DRenderer()
            this.labelRenderer.setSize(window.innerWidth * 90 /100, window.innerHeight * 10 / 100)
            this.labelRenderer.domElement.id = "timerLabel"
            this.labelRenderer.domElement.style.position = "absolute"
            this.labelRenderer.domElement.style.left = "5%"
            this.labelRenderer.domElement.style.top = "10%"
            document.body.appendChild(this.labelRenderer.domElement)

            // Renderer Setup
            this.renderer = new THREE.WebGLRenderer()
            this.renderer.setSize(window.innerWidth * 90 / 100, window.innerHeight * 90 / 100)
            document.body.appendChild(this.renderer.domElement)

            this.renderer.domElement.id = "canvas"
            this.renderer.domElement.style.position = "absolute"
            this.renderer.domElement.style.left = "5%"
            this.renderer.domElement.style.right = "5%"
            this.renderer.domElement.style.top = "10%"

            this.animate()
        },
        animate () {
            requestAnimationFrame(this.animate)
            this.delta = this.clock.getDelta()
            this.auxTime += this.delta
            
            if (!this.won && !this.paused) {
                this.time += this.delta
            }
            this.timerDiv.textContent = "Time: " + this.time.toFixed(0).toString()
            if (!this.won)
                this.pointsDiv.textContent = this.playerPoints.toString() + " : " + this.enemyPoints.toString()
            else
                this.pointsDiv.textContent = "Your score: " + this.score
            this.levelDiv.textContent = "Level: " + this.level.toString()

            if (!this.won && !this.paused) {
                // Check victory
                if (this.level == 6) {
                    this.won = 1
                } else {
                    if (this.enemyPoints == this.levels[this.level - 1]["rounds"])
                    this.won = -1
                }
            }

            if (!this.won && !this.paused) {
                // Level change
                if (this.playerPoints == this.levels[this.level - 1]["rounds"] && this.level < 6){
                    this.level += 1
                    this.playerPoints = 0
                    this.enemyPoints = 0
                    this.backgroundMesh.material.map = this.backgroundSprites[this.level - 1]
                    this.enemyMesh.position.y = 0
                }
            }

            if (!this.won && this.level <= 5 && !this.paused) {
                // Enemy movement
                if (this.enemyMesh.position.y > 2.5)
                    this.enemyDirection *= -1
                if (this.enemyMesh.position.y < -2.5)
                    this.enemyDirection *= -1
                this.enemyMesh.position.y += this.delta * this.enemyDirection * this.levels[this.level - 1]["speed"]

                // Ball movement
                if (this.ballMesh.position.y > 2.75)
                    this.ballDirectionY *= -1
                if (this.ballMesh.position.y < -3.25)
                    this.ballDirectionY *= -1
                this.ballMesh.position.y += this.delta * this.ballDirectionY * this.levels[this.level - 1]["speed"] * (0.5 + this.ballY)
                if (this.ballMesh.position.x > 7) {
                    this.playerPoints += 1
                    this.ballMesh.position.x = 0
                    this.ballMesh.position.y = 0
                    this.ballDirectionX = 1
                    this.ballY = Math.random() * (3 - (-3)) + (-3)
                }
                if (this.ballMesh.position.x < -7) {
                    this.enemyPoints += 1
                    this.ballMesh.position.x = 0
                    this.ballMesh.position.y = 0
                    this.ballDirectionX = -1
                    this.ballY = Math.random() * (3 - (-3)) + (-3)
                }
                this.ballMesh.position.x += this.delta * this.ballDirectionX * 3 * this.levels[this.level - 1]["speed"] * this.levels[this.level - 1]["speed"]

                // Collisions
                var playerBoundingBox = new THREE.Box3().setFromObject(this.playerMesh)
                var enemyBoundingBox = new THREE.Box3().setFromObject(this.enemyMesh)
                var ballBoundingBox = new THREE.Box3().setFromObject(this.ballMesh)
                var collision1 = playerBoundingBox.intersectsBox(ballBoundingBox)
                var collision2 = enemyBoundingBox.intersectsBox(ballBoundingBox)
                if (collision1 == true)
                    this.ballDirectionX = 1
                if (collision2 == true)
                    this.ballDirectionX = -1


                // Player movement
                if (this.keyboard[38]){
                    if (this.playerMesh.position.y < 2.5)
                        this.playerMesh.position.y += this.delta * this.levels[this.level - 1]["speed"] * 3
                }

                if (this.keyboard[40]){
                    if (this.playerMesh.position.y > -2.5)
                        this.playerMesh.position.y -= this.delta * this.levels[this.level - 1]["speed"] * 3
                }
            }

            // Score
            if (this.won == -1 && !this.updatedScore) {
                this.score = Math.floor(this.time / 10)
                this.updateScores()
                this.updatedScore = 1
            }
            if (this.won == 1 && !this.updatedScore) {
                this.score = Math.floor(this.time * 10000 / this.level)
                this.updateScores()
                this.updatedScore = 1
            }

            if (this.keyboard[32]) {
                if (this.won && this.auxTime - this.pressTime > 1) {
                    this.won = 0
                    this.playerPoints = 0
                    this.enemyPoints = 0
                    this.playerMesh.position.y = 0
                    this.enemyMesh.position.y = 0
                    this.ballMesh.position.x = 0
                    this.ballMesh.position.y = 0
                    this.level = 1
                    this.time = 0
                    this.updatedScore = 0
                    this.pressTime = this.auxTime
                    this.backgroundMesh.material.map = this.backgroundSprites[0]
                    this.score = 0
                } else {
                    if (this.paused == 0 && this.auxTime - this.pressTime >= 1) {
                        this.paused = 1;
                        this.pressTime = this.auxTime;
                    } else if (this.paused == 1 && this.auxTime - this.pressTime > 1){
                                this.paused = 0
                                this.pressTime = this.auxTime
                            }
                }   
            }

            this.renderer.render(this.scene, this.camera)
            this.labelRenderer.render(this.scene, this.camera)
        },
        keyDown(event){
            this.keyboard[event.keyCode] = true;
        },
        keyUp(event){
            this.keyboard[event.keyCode] = false;
        },
        resize(event) {
            this.renderer.setSize(window.innerWidth * 90 / 100, window.innerHeight * 90 / 100)
            this.labelRenderer.setSize(window.innerWidth * 90 / 100, window.innerHeight * 10 /100)
            this.camera.aspect = window.innerWidth/ window.innerHeight
        },
        async init_scores() {
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
        async updateScores() {
            const formData = new FormData()
            formData.append('game', this.gameid)
            formData.append('user', this.userid)
            formData.append('score', Math.round(this.score))

            var position = -1 // user does not exist
            for ( var i = 0; i < this.scores.length; i++) {
                if (this.userid == this.scores[i].user) {
                    if (Math.round(this.score) > this.scores[i].score) {
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

                // this.scores.push({'game': this.gameid, 'user': this.userid, 'username': this.user})
                // this.getScore(response.data.id, this.scores.length - 1)
                this.scores = []
                this.init_scores()
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
                    // this.getScore(response.data.id, position)
                    this.scores = []
                    this.init_scores()
                }
            }
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

#scores tr:nth-child(event) {
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