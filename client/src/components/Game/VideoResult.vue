<script>
import {Casts} from "@/enums";

export default {
    name: "VideoResult",
    computed: {
        Casts() {
            return Casts
        }
    },
    props: {
        casts: {
            type: Array,
            required: true,
        },
    },
    methods: {
        runIf(expectedCasts) {
            let expected = new Set(expectedCasts);
            let actual = new Set(this.casts);
            let show = expected.size === actual.size && [...actual].every(x => expected.has(x));
            if (show) {
                this.$refs.videoRef.load();
            }
            return show;
        },
        onVideoEnd() {
            setTimeout(
                () => this.show = false, 1000
            )
        },
        onVideoLoad() {
            this.show = true;
            this.$refs.videoRef.play();
        }
    },
    data() {
        return {
            show: false
        }
    }
}
</script>

<template>
    <video
        autoplay
        muted
        id="myVideo"
        ref="videoRef"
        @ended="onVideoEnd"
        @loadeddata="onVideoLoad"
        :class="show ? 'visible' : 'hidden'"
    >
        <source src="@/assets/video/p-p.mkv" v-if="runIf([Casts.PAPER, Casts.PAPER])" type="video/mp4">
        <source src="@/assets/video/p-r.mkv" v-if="runIf([Casts.PAPER, Casts.ROCK])" type="video/mp4">
        <source src="@/assets/video/r-r.mkv" v-if="runIf([Casts.ROCK, Casts.ROCK])" type="video/mp4">
        <source src="@/assets/video/r-s.mkv" v-if="runIf([Casts.ROCK, Casts.SCISSORS])" type="video/mp4">
        <source src="@/assets/video/s-s.mkv" v-if="runIf([Casts.SCISSORS, Casts.SCISSORS])" type="video/mp4">
        <source src="@/assets/video/s-p.mkv" v-if="runIf([Casts.SCISSORS, Casts.PAPER])" type="video/mp4">
    </video>
</template>

<style scoped>
video {
    max-width: 100%;
    max-height: 100%;
    transition-duration: 0.2s;
    opacity: 1;
}

.hidden {
    opacity: 0;
}

.visible {
    opacity: 1;
}
</style>