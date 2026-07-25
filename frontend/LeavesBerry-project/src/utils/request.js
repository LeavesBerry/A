import api from "./api";
import { showTips } from "./base";
import { userModule } from "./user";

export const apiRequest = {
    async sendCode(email) {
        const res = await api.post('/api/sendCode', { user_email: email });
        return res.data;
    },

    async register(data) {
        const res = await api.post('/api/register', data);
        return res.data;
    },

    async login(data) {
        const res = await api.post('/api/login', data)
        return res.data;
    },

    async logout(data) {
        const res = await api.post('/api/logout', data)
        return res.data;
    },

    async getUserInfo() {
        const res = await api.post('/api/getUserInfo')
        return res.data;
    },

    async submitVisitList(visitList) {
        const res = await api.post('/api/submitVisitList', { visit_list: visitList })
        return res.data
    },

    async initColl(currentUrl) {
        const res = await api.post('/api/initColl', { url: currentUrl });
        return res.data;
    },

    async toggleColl(currentUrl, currentTitle, currentType) {
        const res = await api.post('/api/toggleColl', {
            url: currentUrl,
            title: currentTitle,
            type: currentType
        });
        return res.data;
    },

    async submitFeedback(userEmail, feedback) {
        const res = await api.post('/api/submitFeedBack', {
            user_email: userEmail,
            feedback: feedback
        });
        return res.data
    },

    async getTextResourse(textName) {
        const res = await api.post('/api/getTextResourse', {
            text_name: textName
        });
        return res.data
    }
}

export function disposeReturn(data) {

    if (data.error) {
        showTips(data.error);
        return true;
    }
    if (data.xpChange) {
        userModule.changeXp(data.xpChange)
    }
    if (data.msg) {
        showTips(data.msg);
        return false;
    }
    return false;
}