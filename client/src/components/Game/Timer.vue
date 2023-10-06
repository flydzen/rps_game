<script>
export default {
  name: "Timer",
  props: {
    deadline: {
      type: Number,
      default: null,
    }
  },
  data() {
    return {
      timerCount: 0
    }
  },
  watch: {
    deadline: {
      handler(value) {
        let interval = setInterval(() => {
          let rest = this.deadline === null ? 0 : this.deadline - Date.now() / 1000;
          if (rest <= 0)
            clearInterval(interval)
          else
            this.timerCount = Math.floor(rest);
        }, 1000);
      },
      immediate: true,
    }

  }
}
</script>

<template>
  <p id="timer-p"> {{deadline !== null ? timerCount : '-'}} </p>
</template>

<style scoped>
 #timer-p {
   font-size: 24pt;
 }
</style>