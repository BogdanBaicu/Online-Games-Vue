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
    name: 'EndlessRunner',
    props: ['name', 'gameid','user', 'userid', 'state'],
    mounted () {
        this.init_scores()
        this.init()
    },
    data () {
        return {
            keyboard: {},
            playerSpeed: 0.1,
            spawnPoint: new THREE.Vector3(8, -1.25, 1),
            time: 0,
            sprites: [],
            playerState: 0,
            playerCounter: 0,
            playerJumpedTime: 0,
            playerJumped: 0, 
            collided: 0,
            scores: [],
            updatedScore: 0, 
            paused: 0,
            pressTime: 0,
            auxTime: 0,
            obstacleType: 0
        }
    },
    methods: {
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
        back() {
            this.$emit("changeState", 1)
            document.getElementById('canvas').remove()
            document.getElementById('timerLabel').remove()
            document.getElementById('timerDiv').remove()
        },
        logOut() {
            this.$emit("changeState", 0)
            document.getElementById('canvas').remove()
            document.getElementById('timerLabel').remove()
            document.getElementById('timerDiv').remove()
        },
        highScore() {
            this.$emit("changeState", Number.parseFloat(this.state) + 0.5)
            document.getElementById('canvas').remove()
            document.getElementById('timerLabel').remove()
            document.getElementById('timerDiv').remove()
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
            this.camera.position.y = 1.5
            this.camera.position.z = 5
            this.camera.lookAt(new THREE.Vector3(0, 1, 0))

            // Background
            var textureLoader = new THREE.TextureLoader()
            var backgroundTexture = textureLoader.load("/endless_runner/background2D.jpg")
            backgroundTexture.wrapS = THREE.RepeatWrapping

            this.backgroundMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(20, 10, 100, 100),
                new THREE.MeshBasicMaterial({
                    map: backgroundTexture
                })
            )

            this.backgroundMesh.position.y = 1
            this.scene.add(this.backgroundMesh)

            // Player
            this.sprites.push(textureLoader.load('/endless_runner/1.png'))
            this.sprites.push(textureLoader.load('/endless_runner/2.png'))
            this.sprites.push(textureLoader.load('/endless_runner/3.png'))
            this.sprites.push(textureLoader.load('/endless_runner/4.png'))
            this.playerMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(1, 1, 50, 50),
                new THREE.MeshBasicMaterial({
                    map: this.sprites[this.playerState],
                    transparent: true
                })
            )

            this.playerMesh.position.x = -4.5
            this.playerMesh.position.y = -1.5
            this.playerMesh.position.z = 1
            this.scene.add(this.playerMesh)

            // Obstacle

            this.rock = new THREE.Mesh(
                new THREE.PlaneGeometry(1, 1, 50, 50),
                new THREE.MeshBasicMaterial({
                    map: textureLoader.load('/endless_runner/rock.png'),
                    transparent: true
                })
            )
            this.rock.position.x = this.spawnPoint.x
            this.rock.position.y = this.spawnPoint.y
            this.rock.position.z = this.spawnPoint.z
            this.scene.add(this.rock)

            this.tree = new THREE.Mesh(
                new THREE.PlaneGeometry(1, 1, 50, 50),
                new THREE.MeshBasicMaterial({
                    map: textureLoader.load('/endless_runner/tree.png'),
                    transparent: true
                })
            )
            this.tree.position.x = this.spawnPoint.x
            this.tree.position.y = this.spawnPoint.y
            this.tree.position.z = this.spawnPoint.z
            this.scene.add(this.tree)


            // Text Renderer
            this.timerDiv = document.createElement('div')
            this.timerDiv.id = 'timerDiv'
            this.timerDiv.textContent = 'Time: 0'
            this.timerDiv.style.backgroundColor = "transparent"
            this.timerDiv.style.fontSize = '30px'

            const timerLabel = new CSS2DObject(this.timerDiv)
            timerLabel.position.set(0, 0, 0)
            this.scene.add(timerLabel)
            timerLabel.layers.set(0)

            this.labelRenderer = new CSS2DRenderer()
            this.labelRenderer.setSize(window.innerWidth * 15 / 100, window.innerHeight * 5 / 100)
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

            if (!this.collided) {
                this.delta = this.clock.getDelta()
                if (!this.paused)
                this.backgroundMesh.material.map.offset.x += this.playerSpeed * this.delta
                this.auxTime += this.delta
                if (!this.paused)
                     this.time += this.delta
                this.playerCounter += this.delta
                this.timerDiv.textContent = "Time: " + this.time.toFixed(1).toString()

                // Player Update
                if (this.playerCounter >= 0.2 && !this.paused) {
                    this.playerCounter = 0
                    this.playerState += 1
                    this.playerState %= 4
                    this.playerMesh.material.map = this.sprites[this.playerState]
                }

                // Next obstacle type
                if (this.obstacleType == 0) 
                    this.obstacleType = Math.floor(Math.random() * (2 - 1 + 1) + 1)

                // Increase speed
                if (!this.paused)
                    if (this.keyboard[39]) {
                        if (this.playerSpeed < 0.3) {
                            this.playerSpeed += 2 * this.delta 
                        }
                        this.time += 2 * this.delta
                    } else {
                        if (this.playerSpeed > 0.1) {
                            this.playerSpeed -= 2 * this.delta 
                        }
                    }

                // Jump
                if (!this.paused)
                    if (this.keyboard[38]) {
                        if (this.playerMesh.position.y == -1.5) {
                            this.playerMesh.position.y += 1.5
                            this.playerJumped = 1
                        }
                    }

                if (!this.paused)
                    if (this.keyboard[40] && this.playerJumped) {
                        this.playerJumped = 0
                        this.playerJumpedTime = 0
                        this.playerMesh.position.y -= 1.5
                    }

                if (!this.paused)
                    if (this.playerJumped == 1) {
                        this.playerJumpedTime += this.delta
                        if (this.playerJumpedTime > 1) {
                            this.playerMesh.position.y -= 1.5
                            this.playerJumpedTime = 0
                            this.playerJumped = 0
                        }
                    } 

                this.delta2 = this.delta
                // Obstacle movement
                if (!this.paused && this.obstacleType == 1)
                    this.rock.position.x -= this.playerSpeed * this.delta * 20 * (1 + this.time / 100)

                if (this.rock.position.x < -7) {
                    // this.rock.material.dispose()
                    // this.rock.geometry.dispose()
                    // this.rock.removeFromParent()
                    this.rock.position.x = this.spawnPoint.x
                    this.rock.position.y = this.spawnPoint.y
                    this.rock.position.z = this.spawnPoint.z
                    this.obstacleType = 0
                }

                if (!this.paused && this.obstacleType == 2)
                    this.tree.position.x -= this.playerSpeed * this.delta2 * 20 * (1 + this.time / 100)

                if (this.tree.position.x < -7) {
                    // this.tree.material.dispose()
                    // this.tree.geometry.dispose()
                    // this.tree.removeFromParent()
                    this.tree.position.x = this.spawnPoint.x
                    this.tree.position.y = this.spawnPoint.y
                    this.tree.position.z = this.spawnPoint.z
                    this.obstacleType = 0
                }

                // Player - Obstacle collision
                var playerBoundingBox = new THREE.Box3().setFromObject(this.playerMesh)
                var rockBoundingBox = new THREE.Box3().setFromObject(this.rock)
                var treeBoundingBox = new THREE.Box3().setFromObject(this.tree)
                var collision = playerBoundingBox.intersectsBox(rockBoundingBox)
                var collision2 = playerBoundingBox.intersectsBox(treeBoundingBox)

                if (collision == true || collision2 == true) {
                    this.collided = 1
                }

                this.renderer.render(this.scene, this.camera)
                this.labelRenderer.render(this.scene, this.camera)
            }
            if (this.collided && !this.updatedScore){
                this.updateScores()
                this.updatedScore = 1
            }

            if (this.keyboard[32]) {
                if (this.collided == 1) {
                    this.collided = 0
                    this.updatedScore = 0
                    this.delta = this.clock.getDelta()
                    this.time = 0
                    this.tree.position.x = this.spawnPoint.x + Math.floor(Math.random() * (15 - 5 + 1) + 10)
                    this.rock.position.x = this.spawnPoint.x + Math.floor(Math.random() * (15 - 5 + 1) + 10)
                    this.backgroundMesh.material.map.offset.x = 0
                    this.playerMesh.position.x = -4.5
                    this.paused = 0
                } else {
                    if (this.paused == 0 && this.auxTime - this.pressTime > 1) {
                        this.paused = 1;
                        this.pressTime = this.auxTime;
                    } else if (this.paused == 1 && this.auxTime - this.pressTime > 1){
                                this.paused = 0
                                this.pressTime = this.auxTime
                            }
                                
                }
            }
        },
        keyDown(event){
            this.keyboard[event.keyCode] = true;
        },
        keyUp(event){
            this.keyboard[event.keyCode] = false;
        },
        resize(event) {
            this.renderer.setSize(window.innerWidth * 90 / 100, window.innerHeight * 90 / 100)
            this.labelRenderer.setSize(window.innerWidth * 15 / 100, window.innerHeight * 10 /100)
            this.camera.aspect = window.innerWidth/ window.innerHeight
        },
        async updateScores() {
            const formData = new FormData()
            formData.append('game', this.gameid)
            formData.append('user', this.userid)
            formData.append('score', Math.round(this.time))

            var position = -1 // user does not exist
            for ( var i = 0; i < this.scores.length; i++) {
                if (this.userid == this.scores[i].user) {
                    if (Math.round(this.time) > this.scores[i].score) {
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