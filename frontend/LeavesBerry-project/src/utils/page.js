import { reactive } from "vue";
import Setting from "../pages/Setting.vue";

// 页面状态
export const pageState = reactive({
    isMenuClosed: true,
    isCollected: false,
    isShareClosed: true,
    isCmdClosed: true,
    isTransitioning: false,
    currentUrl: '',
    currentTitle: '',
    currentType: '',
    currentDesc: '',
    showFilter: false,
    leftUp: {},
    leftDown: {},
    rightUp: {},
    rightDown: {},
    menuBox: {},
    navbar: {},
    searchKey: '',
    srcShot: '',
    isScrShot: false,
    shareStyle: {},
    shareText: '➹',
    cmdInputValue: "",
    cmdOutputText: "",
})

export const pageMetaConfig = {
    "Collect": {
        title: "收藏界面",
        type: "other",
        description: '我的收藏'
    },
    "Announce": {
        title: "公告界面",
        type: "essay",
        description: '一些公告'
    },
    "Test2": {
        title: "测试2",
        type: "other",
        description: '用于测试'
    },
    "Protocol": {
        title: "协议界面",
        type: "essay",
        description: '一些访问须知的协议'
    },
    "Feedback": {
        title: "反馈界面",
        type: "other",
        description: '给本站作者反馈'
    },
    "History": {
        title: "历史界面",
        type: "other",
        description: '我的访问历史'
    },
    "CmdColumn": {
        title: "指令表",
        type: "other",
        description: '查看各种指令的用法'
    },
    "Setting": {
        title: "设置界面",
        type: "other",
        description: "设置你的个人资料"
    },
    "Email": {
        title: "邮箱界面",
        type: "other",
        description: "接受和发送站内邮件"
    },
    "Announce/": {
        title: "公告",
        type: "essay",
        description: '一则公告'
    },
    "Email/": {
        title: "邮件",
        type: "essay",
        description: '一则邮件'
    }
}

export const getPageMeta = {
    disposeUrl(url) {
        const slashIndex = url.indexOf('/config_index')
        if (slashIndex === -1) {
            return url
        }
        else {
            return url.slice(0, slashIndex)
        }
    },

    all(url) {
        return pageMetaConfig[this.disposeUrl(url)] ?? {
            title: "未知界面",
            type: "other",
            description: "没有在本站详细注册的界面"
        }
    },

    title(url) {
        return pageMetaConfig[this.disposeUrl(url)]?.title ?? "未知界面"
    },

    type(url) {
        return pageMetaConfig[this.disposeUrl(url)]?.type ?? "other"
    },

    des(url) {
        return pageMetaConfig[this.disposeUrl(url)]?.description ?? "没有在本站详细注册的界面"
    }
}

export function updatePageInfo(pagename, fullPath) {
    const metaInfo = pageMetaConfig[pagename] ?? {
        title: 'LeavesBerry',
        type: 'other',
        description: ''
    }
    pageState.currentUrl = `${fullPath}`;
    pageState.currentTitle = `${metaInfo.title}`;
    pageState.currentType = `${metaInfo.type}`;
    pageState.currentDesc = `${metaInfo.description}`;
}



