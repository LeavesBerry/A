import { useGoPage, showTips, createQRCode, copyText } from "./base"
import { pageState } from "./page"
import { menuModule } from "./menu"
import { navbarModule } from "./navbar"
import { userState } from "./user"
import { ROOTPATH } from "../router"

const { goPage } = useGoPage()


export const cmdHandler = {
    // ------------------------------
    // 路由有关
    // ------------------------------
    tp: function (url) {
        url = url.replace(ROOTPATH, "")
        goPage(url)
        return `已跳转至${url}`
    },
    announce: function (index) {
        if (!index) {
            goPage('/Announce')
            return "已打开公告栏"
        }
        else {
            if (goPage(`/Announce/config_index:${index}`)) {
                return `已打开${index}号公告`
            }
            else {
                return `不存在${index}号公告`
            }
        }
    },
    post: function (index) {
        if (!index) {
            goPage('/Post')
            return "已打开帖子栏"
        }
        else {
            goPage(`/Post/config_index:${index}`)
            return `已打开${index}号帖子`
        }
    },
    collect: function () {
        goPage('/Collect')
        return "已打开收藏夹"
    },
    history: function () {
        goPage('/History')
        return "已打开历史记录"
    },
    // ------------------------------
    // 打印有关
    // ------------------------------
    print: function (item, field) {
        const printableObject = {
            navbar: navbarModule,
            menu: menuModule,
            page: pageState,
            user: userState
        }
        const targetState = printableObject[item]
        if (!targetState) {
            return `不存在名为${item}的可打印字段`
        }
        if (field) {
            return `${item}.${field}的值如下:${JSON.stringify(targetState[field])}`
        }
        else {
            return `${item}的值如下:${JSON.stringify(targetState)}`
        }
    },

    tip: function (text) {
        showTips(text)
        return `已展示${text}`
    },
    qrcode: function (url) {
        createQRCode(url)
        return `已创建${url}的二维码`
    },
    token: function () {
        return `你的token如下:${userState.userAccessToken}\n
        警告:token为你身份的唯一标识,为保证账号安全,请勿泄露!`
    },
    user: function () {
        return `你的用户信息: ${JSON.stringify(userState)}\n
        警告:token为你身份的唯一标识,为保证账号安全,请勿泄露!`
    },
    page: function () {
        return `当前界面信息: ${JSON.stringify(pageState)}`
    },
    // ------------------------------
    // 界面有关
    // ------------------------------
    menu: function (state) {
        switch (state) {
            case '0':
                if (!pageState.isMenuClosed) {
                    menuModule.toggleMenu()
                }
                return "已关闭菜单"
                break
            case '1':
                if (pageState.isMenuClosed) {
                    menuModule.toggleMenu()
                }
                return "已打开菜单"
                break
        }
    },
    // ------------------------------
    // 缓存有关
    // ------------------------------
    clean: function (item) {
        if (item == "all") {
            localStorage.clear()
            return `已移除所有本地储存`
        }
        else if (localStorage.getItem(item)) {
            localStorage.removeItem(item)
            return `已移除本地储存:${item}`
        }
        else {
            return `本地储存:${item}不存在`
        }
    },
    cache: function (item) {
        return `查找的缓存:${JSON.stringify(localStorage.getItem(item))}`
    },
}