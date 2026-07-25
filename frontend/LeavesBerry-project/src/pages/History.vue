<template>
    <div class="slide-page">
        <div id="history-page">
        </div>
    </div>
    <teleport class="fixed-page" to="#app #app-root">
        <Logo></Logo>
    </teleport>
</template>

<script setup>
import { ref } from 'vue';
import Logo from '../components/Logo.vue';
import { api, disposeReturn } from '../utils/index.js';

let historyList = ref([])

async function getHistory() {
    const res = await api.post('/api/getHistory')
    if (!disposeReturn(res.data)) {
        historyList.value = res.data.history
    }
}


</script>