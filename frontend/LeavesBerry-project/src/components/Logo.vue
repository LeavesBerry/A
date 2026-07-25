<template>
    <p class="logo" @click="showTips('本界面著作者:叶果')">@叶果</p>
</template>

<script setup>
import { showTips } from '../utils';
</script>

<style>
.logo {
    font-size: 13px;
    position: fixed;
    z-index: 9999;
    left: 4px;
    bottom: 0;
    color: #c7bea3;
}
</style>
