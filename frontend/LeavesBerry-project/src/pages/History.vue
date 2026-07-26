<template>
    <div class="page" id="history-page">
        <div class="slide-page">
            <p id="title">你的访问历史</p>
            <div id="history-box">
                <ExTextarea v-for="item in historyList" :key="item"
                    :title="pageMetaConfig[item.replace(`/`, '')]?.title ?? '未知界面'" :text="item + '\n' +
                        (pageMetaConfig[item.replace(`/`, '')]?.description ?? '')" custom-class=" textarea"
                    title-class="textarea-title" button-class="textarea-button" content-class="textarea-content">
                </ExTextarea>
            </div>
        </div>
    </div>
    <teleport class="fixed-page" to="#app #app-root">
        <Logo></Logo>
    </teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Logo from '../components/Logo.vue';
import ExTextarea from '../components/ExTextarea.vue'
import api from '../utils/api.js';
import { disposeReturn, pageMetaConfig } from '../utils/index.js';

let historyList = ref([])

async function getHistory() {
    const res = await api.post('/api/getHistory')
    if (!disposeReturn(res.data)) {
        historyList.value = res.data.history.reverse()
    }
}

onMounted(() => {
    getHistory()
})

</script>
<style>
#history-page #title {
    color: #3A251A;
    font-size: 25px;
    font-weight: 700;
    padding-top: calc(4 * var(--design-vh, 4.57px));
}

#history-page #history-box {
    margin-top: calc(4 * var(--design-vh, 4.57px));
}

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