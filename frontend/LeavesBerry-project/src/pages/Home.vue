<template>
	<div class="slide-page">
		<div class="home-page">
			<img src="/icons/logo.png" id="logo">
			<div class="home-divider" id="home-d1"></div>
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
	width: calc(40 * var(--design-vh, 4.57px));
	position: relative;
	margin-top: calc(10 * var(--design-vh, 4.57px));
	user-select: none;
	-webkit-user-select: none;
}

.home-divider {
	width: 100vw;
	border-top: 5px double #3a251a;
	position: relative;
}

#home-d1 {
	margin-top: calc(-1 * var(--design-vh, 4.57px));
}

#home-d2 {
	margin-top: calc(83 * var(--design-vh, 4.57px));
}

.home-star {
	position:absolute;
	top: calc(20 * var(--design-vh, 4.57px));
	font-size: calc(6 * var(--design-vh, 4.57px));
	color: #3a251a;
}

#home-s1 {
	position: absolute;
	left: 8vw;
}

#home-s2 {
	position: absolute;
	left: 32vw;
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
}
</style>