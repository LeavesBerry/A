<template>
    <div class="hidden-container" :style="{
        position:
            configModule.isContentExpanded ? 'absolute' : 'fixed'
    }">
        <div class="content-container" :style="{
            transform: configModule.isContentExpanded ?
                `translateY(calc(-120vh + ${du(10)}))` : 'none'
        }">
            <button class="hide-content-button none-select" @click="configModule.hideContent()">×</button>
            <p class="content-title">{{ configModule.contentTitle }}</p>
            <div class="title-content-divider"></div>
            <p class="content-text" >{{ configModule.contentText }}</p>
        </div>
    </div>
</template>

<script setup>
import { configModule, du } from '../utils';
</script>

<style scoped>
.hidden-container {
    position: fixed;
    top: 120vh;
    left: 5vw;
    width: 90vw;
    height: auto;
    z-index: 9;
    z-index: 9;
}

.content-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 90vw;
    box-shadow: 8px 10px 25px rgb(180, 145, 80, 1);
    background-color: #FFF3D0;
    border-radius: calc(6 * var(--design-vh));
    width: 90vw;
    transition: transform 0.5s ease;
    justify-content: center;
    align-items: center;
    display: flex;
    flex-direction: column;
    display: flex;
}

.content-title {
    width: auto;
    font-size: calc(8 * var(--design-vh));
    color: #3A251A;
    font-weight: 800;
    padding-top: calc(6 * var(--design-vh));
    padding-bottom: calc(6 * var(--design-vh));
}

.content-text {
    width: 83vw;
    height: fit-content;
    color: #3A251A;
    font-weight: 300;
    padding-top: calc(6 * var(--design-vh));
    word-break: break-all;
    word-wrap: break-word;
    white-space: pre-line;
    padding-bottom: 20px;
    text-align: left;
}

.hide-content-button {
    position: absolute;
    top: calc(4.5 * var(--design-vh));
    right: 5%;
    font-size: calc(8 * var(--design-vh));
    background-color: rgba(0, 0, 0, 0);
    border: none;
    color: #3A251A;
}

.title-content-divider {
    width: 84vw;
    height: 0;
    border: 1px solid #3A251A;
}
</style>