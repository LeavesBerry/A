<template>
    <div class="page" id="proto-page">
        <div class="slide-page">
            <div id="sum-box">
                <p id="proto-title">下面长达1mol的协议的概述,阅完此不视为你已阅读下方协议</p>
                <div id="proto-text-box">
                    <p class="proto-text" v-for="(item, index) in protoSumList" :key="`${index}-${item}`">•{{ item }}
                    </p>
                </div>
            </div>
            <div id="detail-box">
                <p id="proto-title">有1mol字的协议正文</p>
                <div id="proto-text-box">
                    <p class="proto-text" id="detail-text">{{ protoDetail }}</p>
                </div>
            </div>
        </div>
    </div>
    <teleport class="fixed-page" to="#app #app-root">
        <Logo></Logo>
    </teleport>
</template>

<script setup>
import Logo from '../components/Logo.vue'
import { apiRequest, disposeReturn } from '../utils'
import { ref, onMounted, onUnmounted } from 'vue'

const protoSumList = ref([])
const protoDetail = ref("")
let isUnmounted = false

function applyProto(data) {
    if (isUnmounted) return

    protoSumList.value = Array.isArray(data?.sum) ? data.sum : []
    protoDetail.value = data?.detail ?? ""
}

async function getProto() {
    const protoCache = localStorage.getItem("proto_cache")

    if (protoCache) {
        try {
            applyProto(JSON.parse(protoCache))
            return
        }
        catch {
            localStorage.removeItem("proto_cache")
        }
    }

    const res = await apiRequest.getTextResourse("proto")
    if (isUnmounted) return

    if (!disposeReturn(res)) {
        applyProto(res)
        localStorage.setItem("proto_cache", JSON.stringify({
            sum: protoSumList.value,
            detail: protoDetail.value
        }))
    }
}

onMounted(async () => {
    await getProto()
})

onUnmounted(() => {
    isUnmounted = true
})
</script>

<style>
#proto-page #proto-title {
    color: #4a4030;
    font-size: 25px;
    font-weight: 700;
    padding-top: calc(4 * var(--design-vh, 4.57px));
}

#proto-page #proto-text-box {
    margin-top: calc(4 * var(--design-vh, 4.57px));
    width: 100vw;
    height: fit-content;
    padding: 20px 0;
    border-top: 1px solid #4a4030;
    border-bottom: 1px solid #4a4030;
}

#proto-page .proto-text {
    position: relative;
    left: 10vw;
    width: 80vw;
    height: fit-content;
    text-align: left;
    color: #4a4030;
    font-size: 15px;
    font-weight: 500;
}

#proto-page #detail-text {
    white-space: pre-line;
    word-break: break-all;
    word-wrap: break-word;
}
</style>
