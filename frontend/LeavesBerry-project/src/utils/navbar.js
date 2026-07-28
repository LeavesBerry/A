import { nextTick, reactive, ref } from "vue"
import { apiRequest, disposeReturn } from "./request"
import { showTips, copyText, createQRCode, du } from "./base"
import { pageState, updatePageInfo } from "./page"
import { cmdHandler } from "./cmd"
import { userState } from "./user"
import { create } from "axios"
import router from "../router"

export const navbarModule = {
    // 搜索
    DoSearch() {
        console.log('搜索:', pageState.searchKey);
    },

    // ------------------------------
    // 截图（懒加载）
    // ------------------------------
    async createScreshot() {
        //import html2canvas from 'html2canvas';
        const canvas = await html2canvas(document, {
            scale: 0.4,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff',
            logging: false,
        });
        pageState.srcShot = canvas.toDataURL('image/jpeg', 1);
        pageState.isScrShot = true;
    },


    // ------------------------------
    // 收藏功能
    // ------------------------------
    async initColl() {
        if (pageState.currentUrl == '') {
            const route = router.currentRoute.value
            updatePageInfo(route.params.page, location.href);
        }
        const collCacheKey = `coll_${pageState.currentUrl}`;
        const cached = localStorage.getItem(collCacheKey);
        if (cached !== null) {
            pageState.isCollected = cached === "true";
            return
        }
        try {
            const res = await apiRequest.initColl(pageState.currentUrl)
            if (!disposeReturn(res)) {
                pageState.isCollected = res.is_collected;
                localStorage.setItem(collCacheKey, res.is_collected)
            }
        } catch (e) {
            showTips(e);
        }
    },

    async toggleColl() {
        if (!userState.isLogined) return
        try {
            pageState.isCollected = !pageState.isCollected;
            userState.isChangedColl = true;
            const res = await apiRequest.toggleColl(pageState.currentUrl,
                pageState.currentTitle, pageState.currentType);
            if (!disposeReturn(res)) {
                pageState.isCollected = res.is_collected;
                localStorage.setItem(`coll_${pageState.currentUrl}`, res.is_collected)
            }
        } catch (e) {
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
                copyText(pageState.currentUrl);
            }
            else {
                createQRCode(pageState.currentUrl);

            }
        }

        pageState.isShareClosed = !pageState.isShareClosed
        if (!pageState.isShareClosed) {
            pageState.shareText = '';
            pageState.shareStyle = {
                width: du(9),
                paddingLeft: du(4.5),
                paddingRight: du(4.5),
                backgroundImage: 'url("http://localhost:5000/static/resource/images/QR.png"),url("http://localhost:5000/static/resource/images/Link.png")',
                backgroundPosition: `${du(1)} center, right ${du(1)} center`,
                backgroundSize: `${du(3)} ${du(3)}, ${du(3)} ${du(3)}`,
                backgroundRepeat: 'no-repeat,no-repeat'
            }
            pageState.shareText = '';


        } else {
            pageState.shareStyle = {};
            pageState.shareText = '➹';
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
        this.showOutput(`运行${cmdName}成功,输出: ${output}`, cmdOutputBox)
    }


};