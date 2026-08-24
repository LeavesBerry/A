import { reactive } from "vue"
import { showTips } from "./base"
import { disposeReturn, apiRequest } from "./request"
import { pageState } from "./page"
import { navbarModule } from "./navbar"
import {
    persistConfig,
    restorePersist,
    setupPersist,
    updatePersistFields,
    removePersistFields
} from "./persist"

const USER_INFO_UPDATED_AT_KEY = "userInfoUpdatedAt"
const USER_INFO_CACHE_DURATION = 10 * 60 * 1000
const DEFAULT_USER_INFO = {
    isLogined: false,
    isChangedColl: false,
    userName: "未登录",
    userId: null,
    userEmail: null,
    bio: "你好,世界!",
    userAccessToken: null,
    avatarUrl: "/static/avatar/default_avatar_1.jpg",
    level: 0,
    xp: 0
}

export const userState = reactive({ ...DEFAULT_USER_INFO })

restorePersist(userState, persistConfig)
setupPersist(userState, persistConfig)

function markUserInfoFresh() {
    localStorage.setItem(USER_INFO_UPDATED_AT_KEY, String(Date.now()))
}

function isUserInfoFresh() {
    const updatedAt = Number(localStorage.getItem(USER_INFO_UPDATED_AT_KEY))
    return Number.isFinite(updatedAt)
        && updatedAt > 0
        && Date.now() - updatedAt < USER_INFO_CACHE_DURATION
}

function clearUserInfoFreshness() {
    localStorage.removeItem(USER_INFO_UPDATED_AT_KEY)
}

export const userModule = reactive({
    getToken() {
        return userState.userAccessToken
    },
    setToken(token) {
        updatePersistFields(userState, { userAccessToken: token }, persistConfig)
    },
    updateUserInfo(data) {
        updatePersistFields(userState, {
            userName: data.user_name,
            userId: data.user_id,
            userEmail: data.user_email,
            bio: data.bio,
            avatarUrl: data.avatar_url,
            level: data.level,
            xp: data.xp,
            isLogined: data.is_logined
        }, persistConfig)
        markUserInfoFresh()
    },
    resetUserInfo() {
        updatePersistFields(userState, { ...DEFAULT_USER_INFO }, persistConfig)
        clearUserInfoFreshness()
        localStorage.clear('coll_list_cache')
    },
    clear() {
        this.resetUserInfo()
        removePersistFields(Object.keys(persistConfig), persistConfig)
        clearUserInfoFreshness()
    },
    async initUser({ forceRefresh = false } = {}) {
        const token = this.getToken()
        if (!token) {
            loginModule.openLoginWindow()
            return
        }
        if (token === "visitor") return
        if (!forceRefresh && userState.isLogined && isUserInfoFresh()) {
            await navbarModule.getAllCollInfo()
            await navbarModule.initColl()
            return
        }
        try {
            const res = await apiRequest.getUserInfo()
            if (disposeReturn(res)) {
                this.clear()
                loginModule.openLoginWindow()
                return
            }
            this.updateUserInfo(res)
            await navbarModule.getAllCollInfo()
            await navbarModule.initColl()
        } catch (error) {
            showTips(error)
            throw error
        }
    },
    async changeBio() { },
    changeXp(change) {
        const oldLevel = userState.level
        const totalXp = 1000 * userState.level + userState.xp + change
        const newLevel = Math.floor(totalXp / 1000)
        const newXp = totalXp % 1000
        updatePersistFields(userState, {
            level: newLevel,
            xp: newXp
        }, persistConfig)
        showTips(change >= 0
            ? `获得${change}点经验`
            : `失去${Math.abs(change)}点经验`)
        if (newLevel > oldLevel) showTips(`恭喜您升级到${newLevel}级`)
    }
})

export const loginModule = reactive({
    inputCode: "",
    inputEmail: "",
    inputName: "",
    inputPw: "",
    window: "",
    memberEntry: {},
    visitorEntry: {},
    memberSign: {},
    infoInput: {},
    isCodeSent: false,
    openLoginWindow() {
        this.window = { display: "block" }
        pageState.showFilter = true
    },
    closeLoginWindow() {
        this.window = { display: "none" }
        pageState.showFilter = false
    },
    visitorEnter() {
        updatePersistFields(userState, {
            userAccessToken: "visitor",
            userId: 0,
            isLogined: false
        }, persistConfig)
        showTips("您已以访客身份进入")
        this.closeLoginWindow()
    },
    memberEnter() {
        this.memberEntry = { transform: "scale(2.04,1)" }
        this.memberSign = { display: "none" }
        this.infoInput = { display: "block" }
        this.visitorEntry = { display: "none" }
    },
    rechoose() {
        this.memberEntry = { transform: "none" }
        this.memberSign = { display: "block" }
        this.infoInput = { display: "none" }
        setTimeout(() => {
            this.visitorEntry = { display: "block" }
        }, 500)
    },
    async sendCode() {
        const email = this.inputEmail
        if (!email) return
        if (!disposeReturn(await apiRequest.sendCode(email))) {
            this.isCodeSent = true
        }
    },
    async login() {
        const data = {
            user_email: this.inputEmail,
            password: this.inputPw
        }
        const res = await apiRequest.login(data)
        if (disposeReturn(res)) return
        userModule.setToken(res.access_token)
        await userModule.initUser({ forceRefresh: true })
        this.rechoose()
        this.closeLoginWindow()
    },
    async logout() {
        try {
            await apiRequest.logout()
        } finally {
            userModule.clear()
            showTips("您已登出")
            this.openLoginWindow()
        }
    },
    async register() {
        if (!this.isCodeSent) {
            await this.sendCode()
            return
        }

        const pw = this.inputPw.trim()
        const email = this.inputEmail.trim()
        const name = this.inputName.trim()
        const code = this.inputCode.trim()

        const checkList = [[code,"验证码"],[email,"邮箱"],[name,"名称"],
            [pw,"密码"]]
        for (const [val,tip] of checkList) {
            if(val.length < 1) {
                showTips(`请填写${tip}`)
                return
            }
        }
        if (!/[a-zA-Z]/.test(pw) || !/[0,9]/.test(pw)) {
            showTips("密码必须同时包含数字和字符")
            return
        }
        if (pw.length < 8) {
            showTips("密码长度必须大于8个字符")
            return
        }
        if (code.length > 6) {
            showTips("验证码异常")
            return
        }
        const data = {
            user_name: name,
            user_email: email,
            code: code,
            password: pw
        }
        const res = await apiRequest.register(data)
        if (!disposeReturn(res)) {
            await this.login()
        }
    },
    
})
