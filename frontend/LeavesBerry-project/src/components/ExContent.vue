<template>
    <div class="hidden-container" :style="{
        position:
            configModule.isContentExpanded ? 'absolute' : 'fixed'
    }">
        <div class="content-container" :style="{
            transform: configModule.isContentExpanded ?
                'translateY(calc(-120vh + var(--navbar-height) + 4 * var(--design-vh))' : 'none'
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
    z-index: 10;
}

.content-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 90vw;
    box-shadow: 8px 10px 25px rgb(180, 145, 80, 1);
    background-color: var(--primary-color);
    border-radius: calc(6 * var(--design-vh));
    width: 90vw;
    transition: transform 0.5s cubic-bezier(0.34,1.56,0.64,1);
    justify-content: center;
    align-items: center;
    display: flex;
    flex-direction: column;
    display: flex;
}

.content-title {
    width: auto;
    font-size: calc(8 * var(--design-vh));
    color: var(--secondary-color);
    font-weight: 800;
    padding-top: calc(6 * var(--design-vh));
    padding-bottom: calc(6 * var(--design-vh));
}

.content-text {
    width: 83vw;
    height: fit-content;
    color: var(--secondary-color);
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
    color: var(--secondary-color);
}

.title-content-divider {
    width: 84vw;
    height: 0;
    border: 1px solid var(--secondary-color);
}
</style>