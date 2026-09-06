import { nextTick} from "vue"
import { apiRequest, disposeReturn, getCollClientId } from "./request"
import { showTips, copyText, createQRCode, du, readLocalArray, sleep } from "./base"
import { pageState, updatePageInfo } from "./page"
import { cmdHandler } from "./cmd"
import { userState } from "./user"
import { ROOTPATH } from "../router"
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
    collState: {
        COLL_INFO_KEY: 'coll_info',
        COLL_URL_KEY: 'coll_url',

        collSSEController: null,
        collSSERunning: false,
        collSSEGeneration: 0,
        collRefreshPromise: null
    },

    async runCollSSE(generation) {

        while (
            this.collState.collSSERunning &&
            generation === this.collState.collSSEGeneration &&
            userState.isLogined
        ) {

            this.collState.collSSEController =
                new AbortController()

            try {

                const response =
                    await fetch(
                        '/api/collSSE',
                        {
                            method: 'GET',

                            headers: {
                                'Accept':
                                    'text/event-stream',

                                'Authorization':
                                    `Bearer ${userState.userAccessToken}`,

                                'X-Client-ID':
                                    getCollClientId()
                            },

                            credentials:
                                'include',

                            cache:
                                'no-store',

                            signal:
                                this.collState.collSSEController.signal
                        }
                    )


                // fetch 不走 Axios interceptor。
                //
                // 如果 access token 过期，
                // 主动用 Axios 请求触发你现有的
                // refreshToken 机制，然后重新连接。
                if (response.status === 401) {

                    try {
                        await navbarModule.getAllColl()
                    }
                    catch {
                        // Axios interceptor 会处理刷新失败
                    }

                    if (!userState.isLogined) {
                        break
                    }

                    throw new Error(
                        'SSE token expired'
                    )
                }


                if (
                    !response.ok ||
                    !response.body
                ) {
                    throw new Error(
                        `SSE error: ${response.status}`
                    )
                }


                // 无论第一次建立还是断线重连，
                // 都重新获取一次完整收藏。
                //
                // 这样断线期间漏掉多少 SSE
                // 都完全没有关系。
                await navbarModule.getAllColl()


                const reader =
                    response.body.getReader()

                const decoder =
                    new TextDecoder()

                let buffer = ''


                while (
                    this.collState.collSSERunning &&
                    generation ===
                        this.collState.collSSEGeneration
                ) {

                    const {
                        value,
                        done
                    } =
                        await reader.read()


                    if (done) {
                        throw new Error(
                            'SSE connection closed'
                        )
                    }


                    buffer +=
                        decoder.decode(
                            value,
                            {
                                stream: true
                            }
                        )


                    // FastAPI SSE 每条事件用 \n\n 分隔
                    let separatorIndex

                    while (
                        (
                            separatorIndex =
                                buffer.indexOf(
                                    '\n\n'
                                )
                        ) !== -1
                    ) {

                        const block =
                            buffer
                                .slice(
                                    0,
                                    separatorIndex
                                )
                                .replace(
                                    /\r/g,
                                    ''
                                )

                        buffer =
                            buffer.slice(
                                separatorIndex + 2
                            )


                        let eventName =
                            'message'

                        const dataLines = []


                        for (
                            const line
                            of block.split('\n')
                        ) {

                            // SSE comment
                            if (
                                line.startsWith(':')
                            ) {
                                continue
                            }


                            if (
                                line.startsWith(
                                    'event:'
                                )
                            ) {

                                eventName =
                                    line
                                        .slice(6)
                                        .trim()
                            }

                            else if (
                                line.startsWith(
                                    'data:'
                                )
                            ) {

                                dataLines.push(
                                    line
                                        .slice(5)
                                        .trimStart()
                                )
                            }
                        }

                        // ----------------------
                        // 收藏发生变化
                        // ----------------------
                        if (
                            eventName ===
                            'coll_changed'
                        ) {

                            // 不相信 SSE 本身保存的数据，
                            // 直接重新拉服务器最终状态。
                            void navbarModule
                                .getAllColl()
                                .catch(error => {
                                    console.error(
                                        '同步收藏失败',
                                        error
                                    )
                                })
                        }

                        // heartbeat 不做任何业务逻辑
                        //
                        // 它只负责保持 HTTP stream 活跃。
                        if (
                            eventName ===
                            'heartbeat'
                        ) {
                            continue
                        }
                    }
                }
            }

            catch (error) {

                if (
                    !this.collState.collSSERunning ||
                    generation !==
                        this.collState.collSSEGeneration
                ) {
                    break
                }

                if (
                    error.name ===
                    'AbortError'
                ) {
                    break
                }

                console.warn(
                    '收藏 SSE 已断开，2 秒后重新连接',
                    error
                )

                await sleep(2000)
            }
        }

        if (
            generation ===
            this.collState.collSSEGeneration
        ) {
            this.collState.collSSERunning = false
            this.collState.collSSEController = null
        }
    },

    connectCollSSE() {

        if (
            !userState.isLogined ||
            this.collState.collSSERunning
        ) {
            return
        }

        this.collState.collSSERunning = true

        const generation =
            ++this.collState.collSSEGeneration

        void runCollSSE(generation)
    },


    disconnectCollSSE() {

        this.collState.collSSERunning = false

        this.collState.collSSEGeneration++

        if (this.collState.collSSEController) {
            this.collState.collSSEController.abort()
            this.collState.collSSEController = null
        }
    },


    clearCollLocal() {

        localStorage.removeItem(
            this.collState.COLL_INFO_KEY
        )

        localStorage.removeItem(
            this.collState.COLL_URL_KEY
        )

        // 顺手清理旧版本
        localStorage.removeItem(
            'coll_info_cache'
        )

        localStorage.removeItem(
            'coll_list_cache'
        )

        pageState.isCollected = false

        window.dispatchEvent(
            new CustomEvent(
                'coll-updated',
                {
                    detail: []
                }
            )
        )
    },

    async getAllColl() {
        if (!userState.isLogined) {
            return []
        }

        // 防止短时间内多个 SSE 同时触发多个完全相同的请求
        if (this.collState.collRefreshPromise) {
            return this.collState.collRefreshPromise
        }

        this.collState.collRefreshPromise = (async () => {

            const res = await api.post('/api/getAllColl')

            const collInfo = Array.isArray(res.data)
                ? res.data
                : []

            const collUrl = collInfo
                .map(item => item.url)
                .filter(Boolean)

            // 详细收藏信息
            localStorage.setItem(
                this.collState.COLL_INFO_KEY,
                JSON.stringify(collInfo)
            )

            // 单独保存 URL，用于 Navbar 快速判断
            localStorage.setItem(
                this.collState.COLL_URL_KEY,
                JSON.stringify(collUrl)
            )

            // 删除以前旧版本留下来的 key
            localStorage.removeItem('coll_info_cache')
            localStorage.removeItem('coll_list_cache')

            // 更新当前页面收藏按钮
            await navbarModule.initColl()

            // 如果当前正打开 Collect.vue，
            // 通知收藏页立刻刷新显示。
            window.dispatchEvent(
                new CustomEvent(
                    'coll-updated',
                    {
                        detail: collInfo
                    }
                )
            )

            return collInfo
        })()

        try {
            return await this.collState.collRefreshPromise
        }
        finally {
            this.collState.collRefreshPromise = null
        }
    },

    async initColl() {
        if (pageState.currentUrl === '') {
            const route = router.currentRoute.value

            updatePageInfo(
                route.params.page,
                location.href.replace(ROOTPATH, '')
            )
        }

        // 未登录不能读取上一个账号残留的收藏状态
        if (!userState.isLogined) {
            pageState.isCollected = false
            return
        }

        const collUrl = readLocalArray(
            this.collState.COLL_URL_KEY
        )

        // 完全本地判断
        pageState.isCollected =
            collUrl.includes(
                pageState.currentUrl
            )
    },

    async toggleColl() {
        if (!userState.isLogined) {
            return
        }

        const oldState = pageState.isCollected

        try {
            // optimistic UI
            pageState.isCollected = !oldState

            const res =
                await apiRequest.toggleColl(
                    pageState.currentUrl,
                    pageState.currentTitle,
                    pageState.currentType,
                    pageState.currentDesc
                )

            if (disposeReturn(res)) {
                pageState.isCollected = oldState
                return
            }

            const isCollected = Boolean(res.is_collected)

            pageState.isCollected = isCollected
                
            let collInfo = readLocalArray(this.collState.COLL_INFO_KEY)

            let collUrl = readLocalArray(this.collState.COLL_URL_KEY)
                

            // ---------------------------
            // 收藏
            // ---------------------------

            if (isCollected) {
                if (
                    !collUrl.includes(
                        pageState.currentUrl
                    )
                ) {
                    collUrl.push(
                        pageState.currentUrl
                    )
                }
                const exists =
                    collInfo.some(
                        item =>
                            item.url ===
                            pageState.currentUrl
                    )
                if (!exists) {
                    collInfo.push({
                        url:
                            pageState.currentUrl,
                        title:
                            pageState.currentTitle,
                        type:
                            pageState.currentType,
                        desc:
                            pageState.currentDesc
                    })
                }
            }

            // ---------------------------
            // 取消收藏
            // ---------------------------

            else {

                collUrl =
                    collUrl.filter(
                        url =>
                            url !==
                            pageState.currentUrl
                    )

                collInfo =
                    collInfo.filter(
                        item =>
                            item.url !==
                            pageState.currentUrl
                    )
            }

            localStorage.setItem(
                COLL_URL_KEY,
                JSON.stringify(collUrl)
            )

            localStorage.setItem(
                COLL_INFO_KEY,
                JSON.stringify(collInfo)
            )

            window.dispatchEvent(
                new CustomEvent(
                    'coll-updated',
                    {
                        detail: collInfo
                    }
                )
            )
        }
        catch (e) {
            pageState.isCollected = oldState
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