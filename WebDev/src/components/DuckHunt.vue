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
import axios from 'axios'
import * as THREE from 'three'
import { CSS2DRenderer, CSS2DObject} from 'three/examples/jsm/renderers/CSS2DRenderer'
export default {
    name: 'DuckHunt',
    props: ['name', 'gameid','user', 'userid', 'state'],
    mounted () {
        this.init()
        this.init_scores()
    },
    data () {
        return{
            keyboard: {},
            time: 10,
            score: 0,
            lifes: [],
            duckIconSprites: [],
            duckIcons: [],
            bullets: [],
            dogSniffSprites: [],
            dogJumpSprites: [],
            dogLaughSprites: [],
            dogState: 0,
            dogCounter: 0,
            duckLSprites: [],
            duckRSprites: [],
            duckTLSprites: [],
            duckTRSprites: [],
            ducks: [],
            dogAnimationDone: 0,
            dogLaugh: 0,
            ducksAdded: 0,
            duckState: 0,
            duckCounter: 0,
            ducksAlive: 3,
            duckHitSprites: [],
            dogCatchSprites: [],
            catchTime: 0,
            catchTime2: 0,
            auxTime: 0,
            pressTime: 0,
            paused: 0,
            scores: [], 
            updatedScore: 0
        }
    },
    methods: {
        init () {
            // Event listeners
            window.addEventListener('resize', this.resize)
            window.addEventListener('keyup', this.keyUp)
            window.addEventListener('keydown', this.keyDown)

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
            this.textureLoader = new THREE.TextureLoader()
            var skyTexture = this.textureLoader.load("/duck_hunt/scene/sky/sky.jpg")
            skyTexture.wrapS = THREE.RepeatWrapping
            this.skyMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(20, 10, 100, 100),
                new THREE.MeshBasicMaterial({
                    map: skyTexture
                })
            )
            this.skyMesh.position.y = 1
            this.scene.add(this.skyMesh)

            var groundTexture = this.textureLoader.load("/duck_hunt/scene/back/0.png")
            this.groundMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(13.25, 7, 50, 50),
                new THREE.MeshBasicMaterial({
                    map: groundTexture,
                    transparent: true
                })
            )
            this.groundMesh.position.y = 1.2
            this.groundMesh.position.z = 1
            this.scene.add(this.groundMesh)

            // UI Renderer
            this.timerDiv = document.createElement('div')
            this.timerDiv.id = 'timerDiv'
            this.timerDiv.textContent = 'Time: 0'
            this.timerDiv.style.backgroundColor = 'transparent'
            this.timerDiv.style.fontSize =  '30px'
            this.timerDiv.style.color = "white"
            const timerLabel = new CSS2DObject(this.timerDiv)
            timerLabel.position.set(0, 0, 0)
            this.scene.add(timerLabel)
            timerLabel.layers.set(0)

            this.scoreDiv = document.createElement('div')
            this.scoreDiv.id = 'scoreDiv'
            this.scoreDiv.textContent = 'Score: 0'
            this.scoreDiv.style.backgroundColor = 'transparent'
            this.scoreDiv.style.fontSize =  '30px'
            this.scoreDiv.style.color = "white"
            const scoreLabel = new CSS2DObject(this.scoreDiv)
            scoreLabel.position.set(0, 2.5, 0)
            this.scene.add(scoreLabel)
            scoreLabel.layers.set(0)

            this.labelRenderer = new CSS2DRenderer();
            this.labelRenderer.setSize(window.innerWidth * 15 / 100, window.innerHeight * 10 /100)
            this.labelRenderer.domElement.style.position = 'absolute'
            this.labelRenderer.domElement.style.top = '10%'
            this.labelRenderer.domElement.style.left = '5%'
            this.labelRenderer.domElement.id = 'timerLabel'
            document.body.appendChild(this.labelRenderer.domElement)

            // Lifes
            this.drawLife(3.25)
            this.drawLife(3.5)
            this.drawLife(3.75)


            // Duck Icons
            this.duckIconSprites.push(this.textureLoader.load('/duck_hunt/hud/score-live/0.png'))
            this.duckIconSprites.push(this.textureLoader.load('/duck_hunt/hud/score-dead/0.png'))
            this.drawDuckIcon(3.25)
            this.drawDuckIcon(3.5)
            this.drawDuckIcon(3.75)
            // this.duckIcons[1].material.map = this.duckIconSprites[0]

            // Bullets
            this.drawBullet(3.25)
            this.drawBullet(3.5)
            this.drawBullet(3.75)
            this.drawBullet(4)

            // Scope
            var scopeTexture = this.textureLoader.load("/duck_hunt/hud/scope/scope.png")
            scopeTexture.wrapS = THREE.RepeatWrapping
            this.scopeMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.25, 0.25, 100, 100),
                new THREE.MeshBasicMaterial({
                    map: scopeTexture,
                    transparent: true
                })
            )
            this.scopeMesh.position.y = 1
            this.scopeMesh.position.z = 1.5
            this.scene.add(this.scopeMesh)

            // Dog
            this.dogCatchSprites.push(this.textureLoader.load('/duck_hunt/dog/double/0.png'))
            this.dogCatchSprites.push(this.textureLoader.load('/duck_hunt/dog/single/0.png'))
            this.dogSniffSprites.push(this.textureLoader.load('/duck_hunt/dog/sniff/0.png'))
            this.dogSniffSprites.push(this.textureLoader.load('/duck_hunt/dog/sniff/1.png'))
            this.dogSniffSprites.push(this.textureLoader.load('/duck_hunt/dog/sniff/2.png'))
            this.dogSniffSprites.push(this.textureLoader.load('/duck_hunt/dog/sniff/3.png'))
            this.dogSniffSprites.push(this.textureLoader.load('/duck_hunt/dog/sniff/4.png'))
            this.dogJumpSprites.push(this.textureLoader.load('/duck_hunt/dog/jump/0.png'))
            this.dogJumpSprites.push(this.textureLoader.load('/duck_hunt/dog/jump/1.png'))
            for (var i = 0; i < 10; i += 1) {
                this.dogLaughSprites.push(this.textureLoader.load('/duck_hunt/dog/laugh/0.png'))
                this.dogLaughSprites.push(this.textureLoader.load('/duck_hunt/dog/laugh/1.png'))
            }

            this.dogMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(1.5, 1.5, 50, 50),
                new THREE.MeshBasicMaterial({
                    map: this.dogSniffSprites[this.dogState],
                    transparent: true
                })
            )

            this.dogMesh.position.x = -4
            this.dogMesh.position.y = -1
            this.dogMesh.position.z = 1.5  
            this.scene.add(this.dogMesh)


            // Ducks
            this.duckLSprites.push(this.textureLoader.load('/duck_hunt/duck/left/0.png'))
            this.duckLSprites.push(this.textureLoader.load('/duck_hunt/duck/left/1.png'))
            this.duckLSprites.push(this.textureLoader.load('/duck_hunt/duck/left/2.png'))
            this.duckRSprites.push(this.textureLoader.load('/duck_hunt/duck/right/0.png'))
            this.duckRSprites.push(this.textureLoader.load('/duck_hunt/duck/right/1.png'))
            this.duckRSprites.push(this.textureLoader.load('/duck_hunt/duck/right/2.png'))
            this.duckTLSprites.push(this.textureLoader.load('/duck_hunt/duck/top-left/0.png'))
            this.duckTLSprites.push(this.textureLoader.load('/duck_hunt/duck/top-left/1.png'))
            this.duckTLSprites.push(this.textureLoader.load('/duck_hunt/duck/top-left/2.png'))
            this.duckTRSprites.push(this.textureLoader.load('/duck_hunt/duck/top-right/0.png'))
            this.duckTRSprites.push(this.textureLoader.load('/duck_hunt/duck/top-right/1.png'))
            this.duckTRSprites.push(this.textureLoader.load('/duck_hunt/duck/top-right/2.png'))
            this.duckHitSprites.push(this.textureLoader.load('/duck_hunt/duck/shot/0.png'))
            this.duckHitSprites.push(this.textureLoader.load('/duck_hunt/duck/dead/0.png'))
            this.duckHitSprites.push(this.textureLoader.load('/duck_hunt/duck/dead/1.png'))
            this.duckHitSprites.push(this.textureLoader.load('/duck_hunt/duck/dead/2.png'))


            // Renderer Setup
            this.renderer = new THREE.WebGLRenderer()
            this.renderer.setSize(window.innerWidth * 90 / 100, window.innerHeight * 90 / 100)
            document.body.appendChild(this.renderer.domElement)

            this.renderer.domElement.id = "canvas"
            this.renderer.domElement.style.position = "absolute"
            this.renderer.domElement.style.left = "5%"
            this.renderer.domElement.style.right = "5%"
            this.renderer.domElement.style.top = "10%"

            this.renderer.domElement.addEventListener('mousemove', this.mouseMove)
            this.renderer.domElement.addEventListener('click', this.mouseClick)

            this.animate()

        },
        animate () {
            requestAnimationFrame(this.animate)

            this.delta = this.clock.getDelta()
            this.auxTime += this.delta

            if (this.dogAnimationDone && this.lifes.length && !this.paused) {
                this.time -= this.delta
                if (this.time > 0) {
                    this.timerDiv.textContent = "Time: " + this.time.toFixed(1).toString()
                    this.scoreDiv.textContent = "Score: " + this.score.toFixed(0).toString()
                } else {
                    this.timerDiv.textContent = "Time: 0"
                    this.scoreDiv.textContent = "Score: " + this.score.toFixed(0).toString()
                }
            }

            // Dog Initial Animation
            this.dogCounter += this.delta
            if (this.dogMesh.position.x < 0 && !this.dogAnimationDone)
                this.dogMesh.position.x += this.delta * 2
            if (this.dogCounter >= 0.1 && this.dogMesh.position.x < 0 && !this.dogAnimationDone) {
                this.dogCounter = 0
                this.dogState += 1
                this.dogState %= 4
                this.dogMesh.material.map = this.dogSniffSprites[this.dogState]
            }
            if (this.dogCounter >= 0.5 && this.dogMesh.position.x >= 0 && this.dogJumpSprites.length && !this.dogAnimationDone && !this.paused) {
                this.dogCounter = 0
                this.dogState += 1
                this.dogState %= 2
                this.dogMesh.material.map = this.dogJumpSprites[this.dogState]
                this.dogMesh.position.y += this.delta * 20
                if (this.dogState == 0)
                    this.dogAnimationDone = 1
            }
            if (this.dogAnimationDone) {
                this.dogMesh.position.x = 7
            }
            if (this.dogLaugh && this.dogState < 20) {
                this.dogMesh.position.x = 3
                this.dogCounter = 0
                this.dogState += 1
                this.dogMesh.material.map = this.dogLaughSprites[this.dogState]
            }

            if (this.dogAnimationDone && !this.ducksAdded) {
                this.drawDuck()
                this.drawDuck()
                this.drawDuck()
                this.ducksAdded = 1
            }

            if (this.ducksAdded && this.lifes.length && !this.paused) {
                this.duckCounter += this.delta
                if (this.duckCounter >= 0.1) {
                    this.duckCounter = 0
                    this.duckState += 1
                    this.duckState %= 3
                }
                for (var i = 0; i < 3; i += 1) {
                    if (this.ducks[i].hit == 0){
                        this.ducks[i].position.x += this.delta * this.ducks[i].speedX * 5
                        this.ducks[i].position.y += this.delta * this.ducks[i].speedY * 0.25
                        if (this.ducks[i].position.x >= 5) {
                            this.ducks[i].orientation -= 1
                            this.ducks[i].speedX *= -1
                        }
                        if (this.ducks[i].position.x <= -5) {
                            this.ducks[i].orientation += 1
                            this.ducks[i].speedX *= -1
                        }
                        if (this.ducks[i].orientation == 1)
                            this.ducks[i].material.map = this.duckLSprites[this.duckState]
                        if (this.ducks[i].orientation == 2)
                            this.ducks[i].material.map = this.duckRSprites[this.duckState]
                        if (this.ducks[i].orientation == 3)
                            this.ducks[i].material.map = this.duckTLSprites[this.duckState]
                        if (this.ducks[i].orientation == 4)
                            this.ducks[i].material.map = this.duckTRSprites[this.duckState]
                    } else {
                        if (this.ducks[i].position.y > -1) {
                            this.ducks[i].position.y -= this.delta * 2
                            this.ducks[i].material.map = this.duckHitSprites[1 + this.duckState]
                        }
                        else {
                            this.ducks[i].position.x = 7
                        } 
                    }   
                }
            }
            if (this.ducksAlive == 1) {
                if (this.catchTime <= 1) {
                    this.catchTime += this.delta
                    this.dogMesh.position.x = 2
                    this.dogMesh.material.map = this.dogCatchSprites[0]
                } else {
                    this.dogMesh.position.x = 7
                }
            }
            if (this.ducksAlive == 0) {
                if (this.catchTime2 <= 1) {
                    this.catchTime2 += this.delta
                    this.dogMesh.position.x = 2
                    this.dogMesh.material.map = this.dogCatchSprites[1]
                } else {
                    this.dogMesh.position.x = 7
                }
            }

            if (this.time && this.ducksAlive == 0 && this.catchTime2 >= 1 && this.lifes.length && !this.paused) {
                // add bonus and reset scene
                this.score += this.time   
                this.score += this.bullets.length
                this.resetScene()             
            }

            if (this.time && this.ducksAlive && this.bullets.length == 0 && this.lifes.length && !this.paused) {
                this.dogLaugh = 1
                if (this.dogState >= 20){
                    this.score -= this.ducksAlive
                    this.loseLife()
                    this.resetScene()
                }
                    
            }

            if (this.time <= 0 && this.lifes.length && !this.paused) {
                if (this.ducksAlive) {
                    this.dogLaugh = 1
                }
                if (this.dogState >= 20) {
                    this.score -= this.ducksAlive
                    this.loseLife()
                    this.resetScene()
                }
                    
            }

            if (this.keyboard[32]) {
                if (this.lifes.length == 0 && this.auxTime - this.pressTime >= 1) {
                    this.time = 10
                    this.score = 0
                    this.resetScene()
                    this.drawLife(3.25)
                    this.drawLife(3.5)
                    this.drawLife(3.75)
                    this.pressTime = this.auxTime;
                    this.updatedScore = 0
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
            
            if (this.lifes.length == 0 && !this.updatedScore) {
                this.updateScores()
                this.updatedScore = 1
            }

            this.renderer.render(this.scene, this.camera)
            this.labelRenderer.render(this.scene, this.camera)
        },
        loseLife() {
            this.lifes[this.lifes.length - 1].material.dispose()
            this.lifes[this.lifes.length - 1].geometry.dispose()
            this.lifes[this.lifes.length - 1].removeFromParent()
            this.scene.remove(this.lifes[this.lifes.length - 1])
            this.lifes.splice(this.lifes.length - 1, 1)
        },
        resetScene(){
            for (var i = 0; i < this.bullets.length; i += 1) {
                this.bullets[i].material.dispose()
                this.bullets[i].geometry.dispose()
                this.bullets[i].removeFromParent()
                this.scene.remove(this.bullets[i])
                this.bullets.splice(i, 1)
                i -= 1
            }

            for (var i = 0; i < this.duckIcons.length; i += 1) {
                this.duckIcons[i].material.dispose()
                this.duckIcons[i].geometry.dispose()
                this.duckIcons[i].removeFromParent()
                this.scene.remove(this.duckIcons[i])
                this.duckIcons.splice(i, 1)
                i -= 1
            }

            for (var i = 0; i < this.ducks.length; i += 1) {
                this.ducks[i].material.dispose()
                this.ducks[i].geometry.dispose()
                this.ducks[i].removeFromParent()
                this.scene.remove(this.ducks[i])
                this.ducks.splice(i, 1)
                i -= 1
            }

            this.drawDuckIcon(3.25)
            this.drawDuckIcon(3.5)
            this.drawDuckIcon(3.75)

            this.drawBullet(3.25)
            this.drawBullet(3.5)
            this.drawBullet(3.75)
            this.drawBullet(4)

            this.drawDuck()
            this.drawDuck()
            this.drawDuck()
            
            this.ducksAlive = 3
            this.time = 10
            this.catchTime = 0
            this.catchTime2 = 0
            this.dogLaugh = 0
            this.dogState = 0
        },
        drawDuck() {
            var speedX = parseFloat((Math.random() * (1 - (-1) + (-1))).toFixed(2))
            var speedY = parseFloat((Math.random() * (2 - (-2) + (-2))).toFixed(2))
            var orientation = 0
            if (speedY < 1)
                if (speedX < 0)
                    orientation = 1
                else
                    orientation = 2
            else
            if (speedX < 0)
                    orientation = 3
                else
                    orientation = 4
            var mesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.5, 0.5, 50, 50),
                new THREE.MeshBasicMaterial({
                    map: this.duckLSprites[0],
                    transparent: true
                })
            )

            if (orientation == 1)
                mesh.material.map = this.duckLSprites[0]
            if (orientation == 2)
                mesh.material.map = this.duckRSprites[0]
            if (orientation == 3)
                mesh.material.map = this.duckTLSprites[0]
            if (orientation == 4)
                mesh.material.map = this.duckTRSprites[0]

            mesh.position.set(
                3.5,
                0,
                1.5
            )
            mesh.speedX = speedX
            mesh.speedY = speedY
            mesh.orientation = orientation
            mesh.hit = 0
            this.scene.add(mesh)
            this.ducks.push(mesh)
        },
        drawLife(positionX) {
            var lifeTexture = this.textureLoader.load("/duck_hunt/hud/heart/0.png")

            var mesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.15, 0.15, 50, 50),
                new THREE.MeshBasicMaterial({
                    map: lifeTexture,
                    transparent: true
                })
            )

            mesh.position.set(
                positionX,
                3.3,
                1.75
            )
            this.scene.add(mesh)
            this.lifes.push(mesh)
        },
        drawDuckIcon(positionX){
            var mesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.25, 0.25, 50, 50),
                new THREE.MeshBasicMaterial({
                    map: this.duckIconSprites[0],
                    transparent: true
                })
            )

            mesh.position.set(
                positionX,
                3.1,
                1.75
            )
            this.scene.add(mesh)
            this.duckIcons.push(mesh)
        },
        drawBullet(positionX) {
            var lifeTexture = this.textureLoader.load("/duck_hunt/hud/bullet/0.png")

            var mesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.15, 0.15, 50, 50),
                new THREE.MeshBasicMaterial({
                    map: lifeTexture,
                    transparent: true
                })
            )

            mesh.position.set(
                positionX,
                2.9,
                1.75
            )
            this.scene.add(mesh)
            this.bullets.push(mesh)
        },
        mouseMove(event) {
            event.preventDefault()

            if (this.mouseX == -1 && this.mouseY == -1) {
                this.mouseX = event.clientX
                this.mouseY = event.clientY
            }

            var vec = new THREE.Vector3()
            var pos = new THREE.Vector3()

            vec.set(
                (event.clientX / window.innerWidth) * 1.1 - 0.5,
                - (event.clientY / window.innerHeight) * 1.1 + 1,
                1.5
            )

            vec.unproject(this.camera)
            vec.sub(this.camera.position).normalize()

            var distance = (-5- this.camera.position.z) / vec.z
            pos.copy(this.camera.position).add(vec.multiplyScalar(distance))
            this.scopeMesh.position.x = pos.getComponent(0)
            this.scopeMesh.position.y = pos.getComponent(1)
        },
        mouseClick(event) {
            if  (event.button == 0 && this.bullets.length && this.lifes.length && !this.paused) {
                this.bullets[this.bullets.length - 1].material.dispose()
                this.bullets[this.bullets.length - 1].geometry.dispose()
                this.bullets[this.bullets.length - 1].removeFromParent()
                this.scene.remove(this.bullets[this.bullets.length - 1])
                this.bullets.splice(this.bullets.length - 1, 1)
                var scopeBoundingBox = new THREE.Box3().setFromObject(this.scopeMesh)
                for (var i = 0; i < 3; i += 1) {
                    var duckBoundingBox = new THREE.Box3().setFromObject(this.ducks[i])
                    var collision = scopeBoundingBox.intersectsBox(duckBoundingBox)
                    if (collision == true) {
                        if (this.ducks[i].hit == 0) {
                            this.ducks[i].hit = 1
                            this.score += 1
                            this.ducksAlive -= 1
                            this.duckIcons[this.ducksAlive].material.map = this.duckIconSprites[1]
                            this.ducks[i].material.map = this.duckHitSprites[0]
                        }
                    }
                }
            }
        },
        resize(event) {
            this.renderer.setSize(window.innerWidth * 90 / 100, window.innerHeight * 90 / 100)
            this.labelRenderer.setSize(window.innerWidth * 15 / 100, window.innerHeight * 10 /100)
            this.camera.aspect = window.innerWidth/ window.innerHeight
        },
        keyDown(event){
            this.keyboard[event.keyCode] = true;
        },
        keyUp(event){
            this.keyboard[event.keyCode] = false;
        },
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