<script setup>
  import Login from './components/Login.vue'
  import Menu from './components/Menu.vue'
  import HighScores from './components/HighScores.vue'
  import Register from './components/Register.vue'
  import ForgotPassword from './components/ForgotPassword.vue'
  import Game from './components/Game.vue'
  import EndlessRunner from './components/EndlessRunner.vue'
  import BalloonMadness from './components/BalloonMadness.vue'
  import DuckHunt from './components/DuckHunt.vue'
  import Pong from './components/Pong.vue'
</script>

<template>
  <div v-if="state == 0">
    <Login @changeState="state = $event" @username="user = $event" @userid="userid = $event"></Login>
  </div>
  <div v-else-if="state == 0.5">
    <Register @changeState="state = $event" @username="user = $event" @userid="userid = $event"></Register>
  </div>
  <div v-else-if="state == 0.7">
    <ForgotPassword @changeState="state = $event" @username="user = $event" @userid="userid = $event"></ForgotPassword>
  </div>
  <div v-else-if="state == 1">
    <Menu @changeState="state = $event" @selectedGame="game = $event" @selectedGameId="gameid = $event"></Menu>
  </div>
  <!-- TODO fiecare joc sa aiba o valoare unica pentru variabila state -->
  <div v-else-if="state == 2">
    <BalloonMadness @changeState="state = $event" :name="game" :gameid="gameid" :user="user" :userid="userid" :state="state"></BalloonMadness>
  </div>
  <div v-else-if="state == 3">
    <EndlessRunner @changeState="state = $event" :name="game" :gameid="gameid" :user="user" :userid="userid" :state="state"></EndlessRunner>
  </div>
  <div v-else-if="state == 4">
    <DuckHunt @changeState="state = $event" :name="game" :gameid="gameid" :user="user" :userid="userid" :state="state"></DuckHunt>
  </div>
  <div v-else-if="state == 5">
    <Pong @changeState="state = $event" :name="game" :gameid="gameid" :user="user" :userid="userid" :state="state"></Pong>
  </div>
  <div v-else-if="Number.isInteger(state)">
    <Game @changeState="state = $event" :name="game" :gameid="gameid" :user="user" :userid="userid" :state="state"></Game>
  </div>
  <div v-else>
    <HighScores @changeState="state = $event" :name="game" :gameid="gameid" :user="user" :userid="userid" :state="state"></HighScores>
  </div>
  
</template>

<script>
  export default {
    componenets: {
      Login,
      Menu,
      HighScores,
      Register,
      ForgotPassword,
      Game,
      EndlessRunner,
      BalloonMadness,
      DuckHunt,
      Pong
    },
    data () {
      return {
        state: 0,
        game: '',
        gameid: '',
        user: '',
        userid: ''
      }
    }
  }
</script>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
