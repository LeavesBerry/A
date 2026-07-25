<template>
	<div class="slide-page">
		<div class="home-page">

			<!--home page-->
			<router-link to="/Collect">CL</router-link>
			<router-link to="/Test2">T2</router-link>
		</div>
	</div>
	<teleport class="fixed-page" to="#app #app-root">
		<Logo></Logo>
	</teleport>
</template>

<script setup lang="ts">
import Logo from '../components/Logo.vue';

</script>