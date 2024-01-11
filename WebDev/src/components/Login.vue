<template>
    <div class="container">
        <h1>Sign In</h1>
        <label><b>Username: </b></label>
        <input type="text" placeholder="Enter Username" id="username">
        <br>
        <label><b>Password: </b></label>
        <input type="password" placeholder="Enter Password" id="password">
        <br>
        <p id="error"></p>
        <button type="button" @click="mainMenu()">Login</button>
        <br>
        <p @click="register()">Don't have an account? Register here!</p>
        <p @click="forgotPassword()">Forgot your password? Recover it!</p>
    </div>
</template>

<script>
    import axios from 'axios'
    export default {
        name: "Login",
        methods: {
            async mainMenu() {
                if (document.getElementById("username").value && document.getElementById("password").value) {
                    const api = axios.create({
                        baseURL: 'http://127.0.0.1:5000',
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        },
                        timeout: 10000
                    })
                    const response1 = await api.get('/searchUserByUsername/' + document.getElementById('username').value)
                    if(response1.data['result'][0] == 0) {
                        document.getElementById("error").textContent = "Username does not exist!"

                        setTimeout(() => {
                            document.getElementById("error").textContent = ""
                        }, 1000)
                    } else {
                        const formData = new FormData()
                        formData.append('username', document.getElementById('username').value)
                        formData.append('password', document.getElementById('password').value)

                        const response = await axios.post('http://127.0.0.1:5000/login',
                            formData,
                            {
                            headers: {
                                'Content-Type': 'multipart/form-data',
                                'Access-Control-Allow-Origin': '*'
                            }, timeout: 10000
                        })
                        if (response.data['result'][0] != 0) {
                            this.$emit("changeState", 1)
                            this.$emit('username', document.getElementById("username").value)
                            this.$emit('userid', response.data['result'][1])
                        } else {
                            document.getElementById("error").textContent = "Credentials don't match!"

                            setTimeout(() => {
                                document.getElementById("error").textContent = ""
                            }, 1000) 
                        }
                        
                    }
                    
                } else {
                    document.getElementById("error").textContent = "Pleae fill in all fields!"

                    setTimeout(() => {
                        document.getElementById("error").textContent = ""
                    }, 1000)
                }
            },
            register() {
                this.$emit("changeState", 0.5)
            },
            forgotPassword() {
                this.$emit("changeState", 0.7)
            }
        }
    }
</script>

<style scoped>
button {
    background-color: #097d28;
    color: white;
    width: 100%;
    border: none;
    cursor: pointer;
    padding: 14px 20px;
    margin: 8px;
}

button:hover {
    opacity: 0.8;
}

input {
    width: 100%;
    padding: 12px 20px;
    margin: 8px;
    background-color: white;
}

#error {
    color: red;
    display: table;
    margin: 0 auto;
}
</style>