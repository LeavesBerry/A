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
    }
}

export function updatePageInfo(pageName, fullPath) {
    const metaInfo = pageName ?
    pageMetaConfig[pageName] ?? {
        title: 'LeavesBerry',
        type: 'other',
        description: '未在本站详细注册的页面'
    } : {
        title: '主页',
        type: 'other',
        description: '本站的开始界面'
    } 
    pageState.currentUrl = `${fullPath}`;
    pageState.currentTitle = `${metaInfo.title}`;
    pageState.currentType = `${metaInfo.type}`;
    pageState.currentDesc = `${metaInfo.description}`;
}



