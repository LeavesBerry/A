<template>
    <div class="expandable-textarea" :class="customClass">
        <p class="title" :class="titleClass">{{ title }}</p>
        <button @click="toggleText" :class="buttonClass">
            {{ isTextExpanded ? "▴" : "▾" }}</button>
        <p class="content" :class="contentClass" v-show="isTextExpanded">{{ text }}</p>
    </div>

</template>

<script setup>
import { ref } from 'vue';

let isTextExpanded = ref(false)

const props = defineProps({
    title: {
        type: String,
        required: true,
        default: () => "未知"
    },
    text: {
        type: String,
        required: true,
        default: () => "未知"
    },
    customClass: String,
    titleClass: String,
    buttonClass: String,
    contentClass: String
});

function toggleText() {
    isTextExpanded.value = !isTextExpanded.value
}
</script>

<style scoped>
.expandable-textarea .content {
    word-break: break-all;
    word-wrap: break-word;
    white-space: pre-line;
    height: auto;
    overflow: visible;
}
</style>