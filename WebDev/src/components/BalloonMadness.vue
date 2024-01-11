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
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer'
import {MTLLoader} from 'three/examples/jsm/loaders/MTLLoader'
import {OBJLoader} from 'three/examples/jsm/loaders/OBJLoader'
export default {
    name: 'BalloonMadness',
    props: ['name', 'gameid','user', 'userid', 'state'],
    mounted () {
        this.init_scores()
        this.init()
    }, 
    data () {
        return {
            gun: [],
            mouseX: -1,
            mouseY: -1, 
            bullets: [],
            balloons: [],
            time: 60,
            score: 0,
            keyboard: {},
            paused: 0,
            pressTime: 0,
            auxTime: 0,
            scores: [], 
            updatedScore: 0
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

            // Light
            this.ambientLight = new THREE.AmbientLight(0xffffff, 0.2)
            this.scene.add(this.ambientLight)

            this.light = new THREE.PointLight(0xffffff, 0.8, 20)
            this.light.position.set(-3, 6, -3)
            this.light.castShadow = true
            this.light.shadow.camera.near = 0.1
            this.light.shadow.camera.far = 25
            this.scene.add(this.light)

            // Ground
            var textureLoader = new THREE.TextureLoader()
            var groundTexture = textureLoader.load('/balloon_madness/grass.jpg', function (texture) {
                texture.wrapS = texture.wrapT = THREE.RepeatWrapping
                texture.offset.set(0, 0)
                texture.repeat.set(50, 50)
            })
            var groundMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(100, 50, 1000, 1000),
                new THREE.MeshPhongMaterial({
                    color: 0xffffff,
                    map: groundTexture
                })
            )
            // TODO rotate ground
            groundMesh.rotateX(- Math.PI/2)
            groundMesh.position.y = -0.5
            groundMesh.receiveShadow = false
            this.scene.add(groundMesh)
            

            // Sky
            var textureLoader = new THREE.TextureLoader()
            var skyTexture = textureLoader.load('/balloon_madness/cumulus-cloud.jpg')
            var skyMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(100, 50, 1000, 1000),
                new THREE.MeshPhongMaterial({
                    color: 0xffffff,
                    map: skyTexture
                })
            );

            skyMesh.position.y = -0.5
            skyMesh.receiveShadow = false
            this.scene.add(skyMesh)

            // Walls
            var wallTexture = textureLoader.load('/balloon_madness/crate0_diffuse.png')
            this.placeWall(wallTexture, 6, 8, 1, 0, 0 , 1)
            this.placeWall(wallTexture, 5, 1, 1, 0, 0 , 4)
            // TODO the other 2 walls
            this.placeWall(wallTexture, 0.1, 8, 0.5, 2.8, 0 , 1.75)
            this.placeWall(wallTexture, 0.1, 8, 0.5, -2.8, 0 , 1.75)

            // // Gun
            // this.drawGun()

            // Balloons
            for ( var i = 0; i < 10; i++) {
                this.drawBalloon()
            }

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

            // Renderer Setup
            this.renderer = new THREE.WebGLRenderer()
            this.renderer.setSize(window.innerWidth * 90 / 100, window.innerHeight * 90 / 100)
            document.body.appendChild(this.renderer.domElement)

            this.renderer.domElement.id = "canvas"
            this.renderer.domElement.style.position = "absolute"
            this.renderer.domElement.style.left = "5%"
            this.renderer.domElement.style.right = "5%"
            this.renderer.domElement.style.top = "10%"

            // this.renderer.domElement.addEventListener('mousemove', this.mouseMove)
            // this.renderer.domElement.addEventListener('click', this.mouseClick)

            // Gun
            this.drawGun()

            this.animate()
        },
        animate() {
            requestAnimationFrame(this.animate)


            this.delta = this.clock.getDelta()
            if ( this.time > 0) {
                this.auxTime += this.delta
                if (!this.paused)
                    this.time -= this.delta
                this.timerDiv.textContent = "Time: " + this.time.toFixed(1).toString()
                this.scoreDiv.textContent = "Score: " + this.score.toFixed(0).toString()

                if (!this.paused) {
                    for (var i = 0; i < this.balloons.length; i++) {
                        var balloonBoundingBox = new THREE.Box3().setFromObject(this.balloons[i])
                        for (var j = 0; j < this.bullets.length; j++) {
                            var bulletBoundingBox = new THREE.Box3().setFromObject(this.bullets[j])
                            var collision = bulletBoundingBox.intersectsBox(balloonBoundingBox)

                            if (collision == true) {
                                this.score += 1
                                var maxX = 1.75
                                var minX = -1.75
                                var maxY = 0
                                var minY = -0.25
                                var maxZ = 3.5
                                var minZ = 1.5
                                this.balloons[i].position.x = parseFloat(Math.random() * (maxX - minX) + minX)
                                this.balloons[i].position.y = parseFloat(Math.random() * (maxY - minY) + minY)
                                this.balloons[i].position.z = parseFloat(Math.random() * (maxZ - minZ) + minZ)
                            }
                        }
                    }
                }
                
                if (!this.paused)
                    for (var i = 0; i < this.balloons.length; i++) {
                        this.balloons[i].position.y += this.balloons[i].speed * this.delta

                        if (this.balloons[i].position.y > 3) {
                            // TODO reset pozitie
                            var maxX = 1.75
                            var minX = -1.75
                            var maxY = 0
                            var minY = -0.25
                            var maxZ = 3.5
                            var minZ = 1.5
                            this.balloons[i].position.x = parseFloat(Math.random() * (maxX - minX) + minX)
                            this.balloons[i].position.y = parseFloat(Math.random() * (maxY - minY) + minY)
                            this.balloons[i].position.z = parseFloat(Math.random() * (maxZ - minZ) + minZ)
                        }
                    }

                if (!this.paused)
                    for (var i = 0; i < this.bullets.length; i++) {
                        this.bullets[i].alive -= this.delta

                        if (this.bullets[i].alive < 0) {
                            this.bullets[i].material.dispose()
                            this.bullets[i].geometry.dispose()
                            this.bullets[i].removeFromParent()
                            this.scene.remove(this.bullets[i])
                            this.bullets.splice(i, 1)
                            i -= 1
                        }
                    }

                if (!this.paused)
                    for (var i = 0; i < this.bullets.length; i++) {
                        this.bullets[i].position.set(
                            this.bullets[i].position.x + this.bullets[i].direction.x * this.delta * 5,
                            this.bullets[i].position.y + this.bullets[i].direction.y * this.delta * 5,
                            this.bullets[i].position.z + this.bullets[i].direction.z * this.delta * 5
                        )
                    }

                this.renderer.render(this.scene, this.camera)
                this.labelRenderer.render(this.scene, this.camera)
            } else {
                this.timerDiv.textContent = "Time: 0"
            }

            if (this.time <= 0 && !this.updatedScore) {
                this.updateScores()
                this.updatedScore = 1
            }
            
            if (this.keyboard[32]) {
                if (this.time <= 0 && this.auxTime - this.pressTime >= 1) {
                    this.time = 60
                    this.score = 0
                    this.updatedScore = 0
                    this.pressTime = this.auxTime;
                    for (var i = 0; i < this.bullets.length; i++) {
                        this.bullets[i].material.dispose()
                            this.bullets[i].geometry.dispose()
                            this.bullets[i].removeFromParent()
                            this.scene.remove(this.bullets[i])
                            this.bullets.splice(i, 1)
                            i -= 1
                    }
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
        },
        keyDown (event) {
            this.keyboard[event.keyCode] = true;
        },
        keyUp (event) {
            this.keyboard[event.keyCode] = false;
        },
        resize(event) {
            this.renderer.setSize(window.innerWidth * 90 / 100, window.innerHeight * 90 / 100)
            this.labelRenderer.setSize(window.innerWidth * 15 / 100, window.innerHeight * 10 /100)
            this.camera.aspect = window.innerWidth/ window.innerHeight
        },
        placeWall(texture, scaleX, scaleY, scaleZ, positionX, positionY, positionZ) {
            var mesh = new THREE.Mesh(
                new THREE.BoxGeometry(scaleX, scaleY, scaleZ),
                new THREE.MeshPhongMaterial({
                    color: 0xffffff,
                    map: texture
                })
            )

            mesh.position.set(positionX, positionY, positionZ)
            mesh.receiveShadow = true
            mesh.castShadow = true

            this.scene.add(mesh)
        },
        drawGun() {
            const scene = this.scene
            const camera = this.camera
            const gun = this.gun
            const renderer = this.renderer
            const mM = this.mouseMove
            const mC = this.mouseClick
            var mtlLoader = new MTLLoader()
            mtlLoader.load('/balloon_madness/uziGold.mtl', function(materials) {
                materials.preload()
                var objLoader = new OBJLoader()
                objLoader.setMaterials(materials)

                objLoader.load('/balloon_madness/uziGold.obj', function(mesh){
                    mesh.scale.setScalar(10)
                    mesh.position.set(camera.position.x, camera.position.y - 0.5, camera.position.z - 0.5)
                    mesh.rotation.set(camera.rotation.x, camera.rotation.y - Math.PI, camera.rotation.z)
                    scene.add(mesh)
                    gun.push(mesh)

                    // TODO
                    renderer.domElement.addEventListener('mousemove', mM)
                    renderer.domElement.addEventListener('click', mC)
                })
            })
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
                (event.clientX / window.innerWidth) * 2 - 1,
                - (event.clientY / window.innerHeight) * 2 + 1,
                0.5
            )

            vec.unproject(this.camera)
            vec.sub(this.camera.position).normalize()

            var distance = (-5- this.camera.position.z) / vec.z
            pos.copy(this.camera.position).add(vec.multiplyScalar(distance))
            this.gun[0].lookAt(pos)
            this.direction = new THREE.Vector3(pos.x - this.gun[0].position.x, 
                                    pos.y - this.gun[0].position.y, 
                                    pos.z - this.gun[0].position.z)
            this.direction.normalize()

        },
        mouseClick(event) {
            if  (event.button == 0)
                this.createBullet()
        },
        createBullet() {
            var mesh = new THREE.Mesh(
                new THREE.SphereGeometry(0.025, 10, 10),
                new THREE.MeshPhongMaterial({
                    color: 0xffffff, 
                })
            )

            mesh.position.set(
                this.gun[0].position.x,
                this.gun[0].position.y  + 0.15,
                this.gun[0].position.z,
            )

            mesh.direction = this.direction
            mesh.alive = 2
            this.scene.add(mesh)
            this.bullets.push(mesh)
        },
        drawBalloon() {
            const scene = this.scene
            const balloons = this.balloons
            var mtlLoader = new MTLLoader()
            mtlLoader.load('/balloon_madness/Balloon.mtl', function(materials) {
                materials.preload()
                var objLoader = new OBJLoader()
                objLoader.setMaterials(materials)

                objLoader.load('/balloon_madness/Balloon.obj', function(mesh){
                    var max = 0.75
                    var min = 0.25
                    mesh.scale.setScalar(parseFloat(Math.random() * (max - min) + min))

                    var maxX = 1.75
                    var minX = -1.75
                    var maxY = 0
                    var minY = -0.25
                    var maxZ = 3.5
                    var minZ = 1.5
                    mesh.position.set(parseFloat(Math.random() * (maxX - minX) + minX), 
                                        parseFloat(Math.random() * (maxY - minY) + minY), 
                                        parseFloat(Math.random() * (maxZ - minZ) + minZ))
                    
                    max = 1
                    min = 0.5
                    mesh.speed = parseFloat(Math.random() * (max - min) + min) * 0.5
                    balloons.push(mesh)
                    scene.add(mesh)
                })
            })
        },
        randNumber(max, min) {
            return parseFloat(Math.random() * (max - min) + min)
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