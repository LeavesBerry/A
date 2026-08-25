<template>
	<div class="slide-page">
		<div class="home-page">
			<Logo logo-class="home-logo" :width="logoSize" :height="logoSize"></Logo>
			<div class="home-divider" id="home-d1"></div>
			<div id="home-icon-box">
				<img class="home-icon" src="/image/home/home_music_icon.png">
				<img class="home-icon" src="/image/home/home_diary_icon.png">
				<img class="home-icon" src="/image/home/home_draw_lots_icon.png">
			</div>
			<div class="home-divider" id="home-d2"></div>
			<span class="home-star none-select" id="home-s1">✦</span>
			<span class="home-star none-select" id="home-s2">✦</span>
			<span class="home-star none-select" id="home-s3">✦</span>
			<span class="home-star none-select" id="home-s4">✦</span>
			<span class="home-star none-select" id="home-s5">✦</span>
			<span class="home-star none-select" id="home-s6">✦</span>
		</div>
	</div>
	<teleport class="fixed-page" to="#app #app-root">
		<Owner></Owner>
	</teleport>
</template>

<script setup>
import Logo from '../components/Logo.vue';
import Owner from '../components/owner.vue';
import { ref } from 'vue';
import { isPortrait } from '../utils/index.js';

const logoSize = ref(isPortrait.value ? '10vh' : '20vh')
</script>

<style>
.home-logo {
	position: relative;
	margin-top: calc(2vh + 8 * var(--design-vh));
	user-select: none;
	-webkit-user-select: none;
}
</style>
<style scoped>
.home-divider {
	width: 100vw;
	border-top: 5px double var(--secondary-color);
	position: relative;
}

#home-d1 {
	margin-top: 0;
}

#home-d2 {
	margin-top: 37vh;
}

.home-star {
	position:absolute;
	top: calc(8.7vh + 8 * var(--design-vh));
	font-size: 6vh;
	color: var(--secondary-color);
}

#home-s1 {
	position: absolute;
	left: 8vw;
}

#home-s2 {
	position: absolute;
	left: 32vw;
	opacity: 1;
}

#home-s3 {
	position: absolute;
	left: 20vw;
}

#home-s4 {
	position: absolute;
	right: 8vw;
}

#home-s5 {
	position: absolute;
	right: 20vw;
}

#home-s6 {
	position: absolute;
	right: 32vw;
	opacity: 1;
}

@media (min-width: 1px) and (orientation: portrait) {
	#home-s2,#home-s6{
		opacity: 0;
	}
	#home-d1 {
		margin-top: 4vh;
	}
	.home-star {
		position:absolute;
		top: calc(7.7vh + var(--navbar-height));
		font-size: 3.5vh;
	}
	.home-logo {
		margin-top: calc(5vh + var(--navbar-height));
		transform: scale(1.8);
	}
}

#home-icon-box {
	width: 100vw;
	height: 6vh;
	position: relative;
	margin-top: 2.5vh;
	display: flex;
	justify-items: center;
	justify-content: center;
}
 
.home-icon {
	height: 40vh;
	width: auto;
	margin: 0 calc(2 * var(--design-vh, 4.57px));
	display: flex;
	transition: scale 0.3s ease;	
}

.home-icon:hover {
	transform: scale(1.05);
}
</style>