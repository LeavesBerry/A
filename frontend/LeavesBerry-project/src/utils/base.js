import { reactive, ref } from "vue";
import { pageState } from "./page";
import { navbarModule } from "./navbar";
import { menuModule } from "./menu";
import * as QRCode from "qrcode"



// ------------------------------
// 常量
// ------------------------------
export const du = (value) => `calc(${value} * var(--design-vh, 4.57px))`
export const isPortrait = ref(window.innerHeight > window.innerWidth)
// ------------------------------
// 工具函数
// ------------------------------

export const tip = reactive({
    tipStyle: {},
    tipText: ''
});
const tipQueue = []
let isShowingTip = false

export function showTips(text) {
    tipQueue.push(text)
    processTipQueue()
}

function processTipQueue() {
    if (isShowingTip || tipQueue.length === 0) {
        return
    }

    isShowingTip = true

    const currentText = tipQueue.shift()
    const showTime = currentText.length * 124 + 890

    tip.tipText = currentText
    tip.tipStyle = {
        visibility: 'visible',
        transform: `translateY(${du(6)})`
    }

    setTimeout(() => {
        tip.tipStyle = {
            visibility: 'hidden',
            transform: 'none'
        }

        isShowingTip = false
        processTipQueue()
    }, showTime)
}

export async function copyText(text) {
    try {
        await navigator.clipboard.writeText(text)
    } catch (err) {
        const area = document.createElement('textarea')
        area.value = text
        document.body.appendChild(area)
        area.select()
        document.execCommand('copy')
        document.body.removeChild(area)
    }
}

export async function createQRCode(url) {
    if (!url.trim()) {
        showTips("创建失败,由于URL值为空")
    }
    const base64Img = await QRCode.toDataURL(url.trim(), {
        width: 220,
        height: 220,
        color: {
            dark: "var(--secondary-color)",
            light: "var(--primary-color)"
        }
    })
    const a = document.createElement('a')
    a.href = base64Img
    a.download = `qrcode_${url}.png`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
}

export function debounce(fn, delay = 100) {
    let timer
    return (...args) => {
        clearTimeout(timer)
        timer = setTimeout(() => fn(...args), delay)
    }
}

export function classifyGroup(data, keyField) {
    const groupMap = new Map();
    for (const item of data) {
        const groupKey = item[keyField]
        if (!groupMap.has(groupKey)) groupMap.set(groupKey, []);
        groupMap.get(groupKey).push(item)
    }
    return groupMap
}

// ------------------------------
// 全局点击关闭
// ------------------------------
export function onGlobalClick(e) {
    const shareBtn = document.querySelector('#share-button');
    const menuBox = document.querySelector('#menu-box');
    const isClickShare = shareBtn?.contains(e.target);
    const isClickMenu = menuBox?.contains(e.target);

    if (!pageState.isShareClosed && !isClickShare) {
        navbarModule.toggleShare();
    }
    if (!pageState.isMenuClosed && !isClickMenu) {
        menuModule.toggleMenu();
    }
}
