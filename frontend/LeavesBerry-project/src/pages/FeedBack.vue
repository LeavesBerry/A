<template>
    <div class="page" id="feedback-page">
        <div class="slide-page">
            <p id="title">对本站的一些建议或想法</p>
            <div id="title-input-devider"></div>
            <textarea id="feedback-input" wrap="soft" :placeholder="placeholder" v-model="feedback"
                :disabled="!couldSubmit">
            </textarea>
            <button id="submit-button" @click="couldSubmit ? submitFeedback() : refreshSubmitCondition()">
                {{ couldSubmit ? "提交反馈" : "刷新冷却" }}</button>
            <div id="tip-box">
                <p v-for="(item, index) in tipList" :key="`${index}-${item}`">•{{ item }}</p>
            </div>
        </div>
    </div>
    <teleport class="fixed-page" to="#app #app-root">
        <Logo></Logo>
    </teleport>
</template>

<script setup>
import { apiRequest, userState, disposeReturn, showTips } from '../utils/index.js';
import { ref, onMounted, onUnmounted } from 'vue';
import Logo from '../components/Logo.vue';

let isUnmounted = false;
const feedback = ref("")
const placeholder = ref("将你的想法或建议写在这里")
const couldSubmit = ref(false)
const FEEDBACK_COLDDOWN_TIME = 24
const tipList = [`${FEEDBACK_COLDDOWN_TIME}小时内只能提交一次反馈`, "请使用中文撰写反馈", "请不要提交垃圾言论",
    "请不要提交空泛,废话式的反馈", "请不要提交不切实际的建议或想法",
    "无法保证你的建议或想法一定被完整采纳", "请不要提交要求过分地遵从你的个人喜好的反馈",
    "以上提示均是为了确保本人将精力花在有价值的反馈上以及避免不必要的争端"
]

function outputSubmitRes(res) {
    if (isUnmounted) return
    showTips(res)
    placeholder.value = res
}

function checkSubmitCondition() {
    if (!userState.isLogined) {
        outputSubmitRes("需登录才能提交反馈")
        return false
    }

    let lastSubmitTime = localStorage.getItem("last_submit_feedback_time")
    if (!lastSubmitTime) return true

    lastSubmitTime = Number(lastSubmitTime)
    if (!Number.isFinite(lastSubmitTime)) {
        localStorage.setItem("last_submit_feedback_time", String(Date.now()))
        outputSubmitRes("参数错误,冷却时间已重置")
        return false
    }

    const waitTime = FEEDBACK_COLDDOWN_TIME * 3600000 - Date.now() + lastSubmitTime
    if (waitTime > 0) {
        outputSubmitRes(`反馈冷却时间还有${(waitTime / 3600000).toFixed(1)}小时`)
        return false
    }

    return true
}

function refreshSubmitCondition() {
    couldSubmit.value = checkSubmitCondition()
}

async function submitFeedback() {
    if (!checkSubmitCondition()) {
        couldSubmit.value = false
        return
    }

    const content = feedback.value.trim()
    if (content.length == 0) {
        outputSubmitRes("请输入文字awa")
        return
    }

    const res = await apiRequest.submitFeedback(userState.userEmail, content)
    if (isUnmounted) return

    if (!disposeReturn(res)) {
        outputSubmitRes("已成功提交反馈")
        feedback.value = ""
        couldSubmit.value = false
        localStorage.setItem("last_submit_feedback_time", String(Date.now()))
    }
}

onMounted(() => {
    couldSubmit.value = checkSubmitCondition()
})

onUnmounted(() => {
    isUnmounted = true
})
</script>

<style>
#feedback-page #title {
    color: #3A251A;
    font-size: 25px;
    font-weight: 700;
    padding-top: calc(4 * var(--design-vh, 4.57px));
}

#feedback-page #feedback-input {
    position: relative;
    margin-top: 20px;
    width: 90.5vw;
    height: fit-content;
    padding: 20px 5px;
    border: 1px solid #4a4030;
    border-bottom: none;
    border-radius: calc(6 * var(--design-vh, 4.57px)) calc(6 * var(--design-vh, 4.57px)) 0 0;
    field-sizing: content;
    min-height: calc(10 * var(--design-vh, 4.57px));
    max-height: calc(300 * var(--design-vh, 4.57px));
    resize: none;
    overflow-y: hidden;
    background-color: rgba(0, 0, 0, 0);
    height: fit-content;
    color: #3A251A;
    font-size: 20px;
    font-weight: 300;
    text-align: top;
    word-break: break-all;
    word-wrap: break-word;
    overflow-x: hidden;
}

#feedback-page #feedback-input::placeholder {
    color: #4a4030;
}

#feedback-page #submit-button {
    position: relative;
    margin-top: -1px;
    padding: 0, 5px;
    width: 90.5vw;
    height: calc(8 * var(--design-vh, 4.57px));
    background-color: rgba(0, 0, 0, 0);
    border: 1px solid #4a4030;
    border-radius: 0 0 calc(6 * var(--design-vh, 4.57px)) calc(6 * var(--design-vh, 4.57px));
    font-size: 20px;
    font-weight: 600;
    color: #3A251A;
    cursor: pointer;
}

#feedback-page #tip-box {
    position: absolute;
    left: 5vw;
    width: 90vw;
    margin-top: calc(2 * var(--design-vh, 4.57px));
    justify-items: left;
}

#feedback-page #tip-box p {
    color: #4a4030;
    font-size: 15px;
    font-weight: 500;
}
</style>
