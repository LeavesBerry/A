import { nextTick, reactive, ref } from "vue"
import { apiRequest, disposeReturn } from "./request"
import { showTips, copyText, createQRCode, du } from "./base"
import { pageState, updatePageInfo } from "./page"
import { cmdHandler } from "./cmd"
import { userState } from "./user"
import { ROOTPATH } from "../router"
import { create } from "axios"
import router from "../router"
import api from "./api"

export const navbarModule = {
    // 搜索
    DoSearch() {
        console.log('搜索:', pageState.searchKey);
    },

    // ------------------------------
    // 截图（懒加载）
    // ------------------------------
    async cleanScreenShot() {
        URL.revokeObjectURL(pageState.srcShot)
        pageState.isSrcShot = false;
        pageState.srcShot = '';
        pageState.showFilter = false;
        window.gc?.();
    },

    async createScreenshot() {
        const targetDom = document.documentElement;
        if (!targetDom) {
            alert("界面异常,截图失败")
            return
        }
        let canvas = null
        try {
            const html2canvas = (await import ('html2canvas')).default;
            canvas = await html2canvas(targetDom, {
                useCORS: true,
                scale: Math.min(window.devicePixelRatio, 2),
                useCORS: true,
                allowTaint: true,
                backgroundColor: '#ffffff',
                logging: false,
                width: document.documentElement.clientWidth,
                height: document.documentElement.clientHeight,
                x: window.scrollX,
                y: window.scrollY
            });
            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.75));
            const imgUrl =URL.createObjectURL(blob);
            pageState.srcShot = imgUrl;
            pageState.isSrcShot = true;
            pageState.showFilter = true
        } catch(e) {
            this.cleanScreenShot()
            console.log(e)
        } finally {
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0,0,canvas.width, canvas.height);
                canvas.width = canvas.height = 0
                canvas = null;
            }
        }
    },

    // ------------------------------
    // 收藏功能
    // ------------------------------
    async initColl(url = pageState.currentUrl) {
        if (url == '') {
            const route = router.currentRoute.value
            updatePageInfo(route.params.page, location.href.replace(ROOTPATH,''));
        }
        const res = await apiRequest.initColl(url);
        pageState.isCollected = res.is_collected ?? false
    },

    async toggleColl() {
        if (!userState.isLogined) return
        const oldState = pageState.isCollected
        try {
            pageState.isCollected = !oldState;
            const res = await apiRequest.toggleColl(pageState.currentUrl,
                pageState.currentTitle, pageState.currentType, pageState.currentDesc);
            if (!disposeReturn(res)) {
                const isCollected = res.is_collected
                pageState.isCollected = isCollected;
            }
        } catch (e) {
            pageState.isCollected = oldState
            console.log(e)
            showTips(e)
        }
    },

    // ------------------------------
    // 分享功能
    // ------------------------------

    toggleShare(e) {

        if (!pageState.isShareClosed && e) {
            const btn = document.querySelector('#share-button');
            const rect = btn.getBoundingClientRect();
            if (e.clientX - rect.left >= rect.width / 2) {
                copyText(ROOTPATH + pageState.currentUrl);
            }
            else {
                createQRCode(ROOTPATH + pageState.currentUrl);

            }
        }

        pageState.isShareClosed = !pageState.isShareClosed
        if (!pageState.isShareClosed) {
            pageState.shareStyle = {
                width: du(9),
                paddingLeft: du(1.1),
                paddingRight: du(1.1),
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
            }
        } else {
            pageState.shareStyle = {};
        }
    },

    // ------------------------------
    // 命令面板
    // ------------------------------
    toggleCmdUI() {
        pageState.isCmdClosed = !pageState.isCmdClosed;
    },

    showOutput(text, cmdOutputBox) {
        pageState.cmdOutputText += `${text}\n`;
        nextTick(() => {
            if (cmdOutputBox) {
                cmdOutputBox.scrollTop = cmdOutputBox.scrollHeight;
            }
        })
    },

    executeCmd(cmdOutputBox) {
        const cmd = pageState.cmdInputValue;
        const reg = /^([a-zA-Z0-9_]+)\((.*)\)$/
        const match = cmd.trim().match(reg)
        if (!match) {
            this.showOutput("指令格式错误", cmdOutputBox)
            return
        }
        const cmdName = match[1]
        const argsRaw = match[2]
        const args = argsRaw.split(',').map(arg => arg.trim())
        const handler = cmdHandler[cmdName]
        if (typeof handler !== 'function') {
            this.showOutput(`未知指令：${cmdName}`, cmdOutputBox);
            return
        }
        const output = handler(...args)
        pageState.cmdInputValue = ""
        this.showOutput(`运行${cmdName}成功,输出 | ${output}`, cmdOutputBox)
    }


};