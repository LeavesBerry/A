<template>
    <div class="page" id="draw-lots-page">
        <div id="wifi-tip-window" v-if="!isAgreeLoadOnMD && !isWiFiConnection">
            <p id="wifi-tip">当前界面需要加载较多的图片资源,约10MB!<br>
                检测到你当前可能处于非WiFi环境下,可能造成流量开销，是否确认加载？</p>
            <button id="confirm-MD-load-button" @click="isAgreeLoadOnMD = true">确认</button>
            <button id="cancel-MD-load-button" @click="isAgreeLoadOnMD = false; backPage()">取消</button>
        </div>
        <div v-if="isAgreeLoadOnMD || isWiFiConnection">
            <div v-if="mode == 'single'">
                <img id="lot-img" :style="singleDrawModule.lotImgStyle" 
                    :src="singleDrawModule.lotImgSrc">
                <p id="lot-title" :style="singleDrawModule.lotTitleStyle">
                    {{ singleDrawModule.lotTitle }}</p>
                <p id="lot-text" :style="singleDrawModule.lotTextStyle" v-if="isInterpretExpanded">
                    {{ singleDrawModule.lotText }}</p>
            </div>

            <img id="draw-lots-background-image" src="/image/drawlots/background.jpg">
            
            <button id="draw-lots-button" @click="mode == 'single' ? singleDrawModule.drawLot()
            : console.log(1)"></button>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue';
import { showTips, useGoPage } from '../utils/index';

const { backPage } = useGoPage()

const isAgreeLoadOnMD = ref(false)
const isWiFiConnection = ref(false)
const isResLoaded = false

const mode = ref('')
const isInterpretExpanded = ref(false)

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

const singleDrawModule = reactive({
    lotImgStyle: {},
    lotImgSrc: '',
    lotTitleStyle: {},
    lotTitle: '',
    lotTextStyle: {},
    lotText: '',
    drawLot() {
        const lotTexts = await fetch('/text/lots/lot_text.json')
        const lotTextList = lotTexts.json()
        const lotIndex = Math.floor(Math.random() * (lotTextList.length))
        const lot = lotTextList[lotIndex] 
        const position = Math.random() < 0.5 ? 'reversed' : 'upright'
        this.lotTitle = lot['name'] + '\n' + position == 'upright' ? '正位' : '逆位'
        this.lotText = lot[position]
        this.lotImgSrc = `/image/lot/lot_${lotIndex}.png`
    },
    InterpretLot() {
        if(window.innerHeight < (window.innerWidth * 0.9)) {
            this.lotImgStyle = {
                transform: 'translateX(30vw) scale(1.2) translateY(10vh)'
            }
            this.lotTitleStyle = {
                transform: 'translateY(30vh)'
            }
        }
        setTimeout(() => {
            isInterpretExpanded.value = true
        }, 500)
    }
})

if(navigator.connection) {
    navigator.connection.addEventListener('change', () => {
        if (!isAgreeLoadOnMD && !isResLoaded) {
            showTips("网络切换,正在重新检测")
            checkConnection()
        }
    })
}

onMounted(() => {
    checkConnection()
})
</script>