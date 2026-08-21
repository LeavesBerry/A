<template>
	<div class="slide-page">
		<div class="home-page">
			<img src="/icon/logo.png" id="logo">
			<div class="home-divider" id="home-d1"></div>
			<div id="home-icon-box">
				<img class="home-icon" src="/image/HomeMusicIcon.png">
				<img class="home-icon" src="/image/HomeDiaryIcon.png">
				<img class="home-icon" src="/image/HomeGoodIcon.png"> 
			</div>
			<div class="home-divider" id="home-d2"></div>
			<span class="home-star" id="home-s1">✦</span>
			<span class="home-star" id="home-s2">✦</span>
			<span class="home-star" id="home-s3">✦</span>
			<span class="home-star" id="home-s4">✦</span>
			<span class="home-star" id="home-s5">✦</span>
			<span class="home-star" id="home-s6">✦</span>
		</div>
	</div>
	<teleport class="fixed-page" to="#app #app-root">
		<Logo></Logo>
	</teleport>
</template>

<script setup lang="ts">
import Logo from '../components/Logo.vue';

</script>

<style scoped>
#logo {
	height: 15vh;
	position: relative;
	margin-top: calc(2vh + 8 * var(--design-vh));
	user-select: none;
	-webkit-user-select: none;
}

.home-divider {
	width: 100vw;
	border-top: 5px double #3a251a;
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
	top: calc(7.7vh + 8 * var(--design-vh));
	font-size: 3.5vh;
	color: #3a251a;
}

#home-s1 {
	position: absolute;
	left: 8vw;
}

#home-s2 {
	position: absolute;
	left: 32vw;
	opacity: 0;
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
	opacity: 0;
}


@media (min-width: 1px) and (orientation: landscape) {
	#home-s2,#home-s6{
		opacity: 1;
	}
	#logo {
		height: 20vh;
	}
	.home-star {
		position:absolute;
		top: calc(8.7vh + 8 * var(--design-vh));
		font-size: 6vh;
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