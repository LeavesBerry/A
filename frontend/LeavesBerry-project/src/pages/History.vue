<template>
    <div class="page" id="history-page">
        <div class="slide-page">
            <div class="item-box">
                <div class="item" id="history" v-for="item in currentContent">
                    <p class="item-title" id="history-title">
                        {{ pageMetaConfig[item.replace(`/`, '')]?.title ?? '未知界面' }}</p>
                    <p id="history-url">{{ ROOTPATH + item }}</p>
                    <p id="history-des">
                        {{ pageMetaConfig[item.replace(`/`, '')]?.description ?? '' }}</p>
                </div>
            </div>

        </div>
    </div>
    <teleport class="fixed-page" to="#app #app-root">
        <Logo></Logo>
        <Sidebar type-list="historyTypeList" @change-dir=""></Sidebar>
    </teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Logo from '../components/Logo.vue';
import Sidebar from '../components/Sidebar.vue';
import ExTextarea from '../components/ExTextarea.vue'
import api from '../utils/api.js';
import { disposeReturn, pageMetaConfig, currentSidebarConfig } from '../utils/index.js';
import { ROOTPATH } from '../router/index.js';

const historyTypeList = [
    { index: 0, typeKey: "all", label: "所有", id: "all" },
    { index: 1, typeKey: "recent", label: "较近", id: "recent" },
    { index: 2, typeKey: "past", label: "较远", id: "past" }
]
let currentContent = ref([])

let historyList = ref([])

async function getHistory() {
    const res = await api.post('/api/getHistory')
    if (!disposeReturn(res.data)) {
        historyList.value = res.data.history.reverse()
    }
}

function switchDirContent(sn, type) {
    currentSidebarConfig.value = sn

    switch (type) {
        case "all":
            currentContent.value = historyList.value
            return
        case "recent":
            currentContent.value = historyList.value.slice(0, 30)
            return
        case "past":
            currentContent.value = historyList.value.slice(30)
    }
}

onMounted(() => {
    currentSidebarConfig.value = 0
    getHistory()
})

</script>
<style scoped>
#history-box {
    margin-top: calc(4 * var(--design-vh, 4.57px));
}
</style>
<style>
#history-page .textarea {
    width: 90.5vw;
    height: auto;
    flex-direction: column;
    padding-top: calc(1 * var(--design-vh));
    padding-bottom: calc(2 * var(--design-vh));
    position: relative;
    margin-top: 0;
    display: flex;
    text-decoration: none;
    z-index: 2;
    -webkit-user-select: none;
    user-select: none;
    background-color: rgba(0, 0, 0, 0);
    border: 1px solid #3A251A;
    border-bottom: none;
}

#history-page .textarea:first-child {
    border-radius: calc(6 * var(--design-vh)) calc(6 * var(--design-vh)) 0 0;
}

#history-page .textarea:last-child {
    border-radius: 0 0 calc(6 * var(--design-vh)) calc(6 * var(--design-vh));
    border-bottom: 1px solid #3A251A;
}

#history-page .textarea-title {
    width: fit-content;
    height: auto;
    font-size: calc(4 * var(--design-vh));
    color: #3A251A;
    font-weight: 400;
    position: relative;
    top: 0;
    left: 7%;
}

#history-page .textarea-button {
    position: absolute;
    right: 5%;
    top: calc(-2 * var(--design-vh));
    height: calc(10 * var(--design-vh));
    width: auto;
    background: none;
    border: none;
    font-size: calc(10 * var(--design-vh));
    font-weight: 500;
    color: #3A251A;
}

#history-page .textarea-content {
    position: relative;
    left: 7%;
    top: 8px;
    width: 86%;
    height: fit-content;
    padding-top: 1.5px;
    border-top: 1px solid #3A251A;
    color: #3A251A;
    text-align: left;
}
</style>