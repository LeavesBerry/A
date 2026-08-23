<template>
    <div class="page" id="draw-lots-page">
        <div id="wifi-tip-window" v-if="!isAgreeLoadOnMD && !isWiFiConnection">
            <p id="wifi-tip">当前界面需要加载较多的图片资源,约10MB!<br>
                检测到你当前可能处于非WiFi环境下,可能造成流量开销，是否确认加载？</p>
        </div>
        <div v-if="isAgreeLoadOnMD || isWiFiConnection"></div>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { showTips } from '../utils/index';

const isAgreeLoadOnMD = ref(false)
const isWiFiConnection = ref(false)

function checkConnection() {
    const net = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if(!net) {
        isWiFiConnection.value = false
        return
    }

    switch (net) {
        case "wifi":
            isWiFiConnection.value = true
            return;
        case "cellular":
            isWiFiConnection.value = false
            return
        default:
            isWiFiConnection.value = false
            return
    }
}

if(navigator.connection) {
    navigator.connection.addEventListener('change', () => {
        if (!isAgreeLoadOnMD) {
            showTips("网络切换,正在重新检测")
            checkConnection()
        }
    })
}

onMounted(() => {
    checkConnection()
})
</script>