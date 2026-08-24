<template>
    <div class="page" id="draw-lots-page">
        <div id="wifi-tip-window" v-if="!isAgreeLoadOnMD && !isWiFiConnection">
            <p id="wifi-tip">当前界面需要加载较多的图片资源,约10MB!<br>
                检测到你当前可能处于非WiFi环境下,可能造成流量开销，是否确认加载？</p>
            <button id="confirm-MD-load-button" @click="isAgreeLoadOnMD = true">确认</button>
            <button id="cancel-MD-load-button" @click="isAgreeLoadOnMD = false; backPage()">取消</button>
        </div>
        <div v-if="isAgreeLoadOnMD || isWiFiConnection">
            <img id="draw-lots-background-image" src="/image/drawlots/background.jpg">
            <img v-for="index in 18" :key="index" :src="`/image/drawlots/lot${index}`" 
            v-show="currentLotIndex == index">
            <p id="oracle-text">{{ currentOracleText }}</p>
            <button id="draw-lots-button" @click="drawLots"></button>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { showTips, useGoPage } from '../utils/index';

const { backPage } = useGoPage()

const isAgreeLoadOnMD = ref(false)
const isWiFiConnection = ref(false)

const currentLotIndex = ref(0)
const currentOracleText = ref('')

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

async function drawLots() {
    const lotIndex = Math.floor(Math.random() * 18)
    const oracleTexts = await fetch('/text/lots/oracle_text.json')
    const oracleTextList = oracleTexts.json()
    currentLotIndex.value = lotIndex
    currentOracleText.value = oracleTextList[lotIndex]
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