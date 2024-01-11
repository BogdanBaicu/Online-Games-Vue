<template>
    <div class="container">
        <h1>Sign In</h1>
        <label><b>First Name: </b></label>
        <input type="text" placeholder="Enter First Name" id="firstName">
        <br>
        <label><b>Last Name: </b></label>
        <input type="text" placeholder="Enter Last Name" id="lastName">
        <br>
        <label><b>Username: </b></label>
        <input type="text" placeholder="Enter Username" id="username">
        <br>
        <label><b>Email: </b></label>
        <input type="email" placeholder="Enter Email" id="email">
        <br>
        <label><b>Password: </b></label>
        <input type="password" placeholder="Enter Password" id="password">
        <br>
        <label><b>Confirm Password: </b></label>
        <input type="password" placeholder="Confirm Password" id="confirmPassword">
        <br>
        <p id="error"></p>
        <button type="button" @click="mainMenu()">Register</button>
        <br>
    </div>
</template>

<script>
    import axios from 'axios'
    export default {
        name:"Register",
        methods: {
            async mainMenu(){
                if (document.getElementById("firstName").value &&
                    document.getElementById("lastName").value &&
                    document.getElementById("username").value &&
                    document.getElementById("email").value &&
                    document.getElementById("password").value &&
                    document.getElementById("confirmPassword").value) {
                        if (String(document.getElementById("password").value).length < 6) {
                            document.getElementById("error").textContent = "Password too short!"

                            setTimeout(() => {
                                document.getElementById("error").textContent = ""
                            }, 1000)
                        } else {

                            if (document.getElementById("password").value == document.getElementById("confirmPassword").value) {
                                const api = axios.create({
                                    baseURL: 'http://127.0.0.1:5000',
                                    headers: {
                                        'Content-Type': 'multipart/form-data'
                                    },
                                    timeout: 10000
                                })
                                const response1 = await api.get('/searchUserByUsername/' + document.getElementById('username').value)
                                if(response1.data['result'][0] != 0) {
                                    document.getElementById("error").textContent = "Username already exists!"

                                    setTimeout(() => {
                                        document.getElementById("error").textContent = ""
                                    }, 1000)
                                }
                                const response2 = await api.get('/searchUserByEmail/' + document.getElementById('email').value)
                                if(response2.data['result'][0] != 0) {
                                    document.getElementById("error").textContent = "Email already exists!"

                                    setTimeout(() => {
                                        document.getElementById("error").textContent = ""
                                    }, 1000)
                                }

                                if (response1.data['result'][0] == 0 && response2.data['result'][0] == 0) {
                                    const formData = new FormData()
                                    formData.append('username', document.getElementById("username").value)
                                    formData.append('firstName', document.getElementById("firstName").value)
                                    formData.append('lastName', document.getElementById("lastName").value)
                                    formData.append('email', document.getElementById("email").value)
                                    formData.append('password', document.getElementById("password").value)
                                    formData.append('confirmPassword', document.getElementById("confirmPassword").value)

                                    const response = await axios.post('http://127.0.0.1:5000/register',
                                        formData,
                                        {
                                        headers: {
                                            'Content-Type': 'multipart/form-data'
                                        }
                                    })


                                    this.$emit("changeState", 1)
                                    this.$emit('username', document.getElementById("username").value)
                                    this.$emit('userid', response1.data['result'][1])
                                }
                                
                            } else {
                                document.getElementById("error").textContent = "Passwords don't match!"

                                setTimeout(() => {
                                    document.getElementById("error").textContent = ""
                                }, 1000)
                            }
                        }
                } else {
                    document.getElementById("error").textContent = "Please fill in all fields!"

                    setTimeout(() => {
                        document.getElementById("error").textContent = ""
                    }, 1000)
                }
                    
            }
        }
    }
</script>

<style scoped>
button {
    background-color: #087d28;
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