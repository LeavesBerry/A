import api from "./api";
import { showTips } from "./base";
import { userModule } from "./user";

const COLL_CLIENT_ID =
    globalThis.crypto?.randomUUID?.()
    ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;


export function getCollClientId() {
    return COLL_CLIENT_ID;
}

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

    async refreshColl(currentUrl, currentTitle, currentType, currentDesc) {
        const res = await api.post('/api/refreshColl', { 
            url: currentUrl,
            title: currentTitle,
            type: currentType,
            desc: currentDesc
        });
        return res.data;
    },

    async toggleColl(currentUrl, currentTitle, currentType, currentDesc) {
        const res = await api.post('/api/toggleColl', {
            url: currentUrl,
            title: currentTitle,
            type: currentType,
            desc: currentDesc
        },
        {
            headers: {
                'X-Client-ID': getCollClientId()
            }
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
    },

    async changeBio(bio) {
        const res = await api.post('/api/changeBio', {
            bio: bio
        });
        return res.data
    },

    async changeAvatar(blob) {
        const formData = new FormData()
        formData.append("file", blob, 'avatar_img.jpg')
        const res = await api.post('/api/changeAvatar', formData);
        return res.data
    },

    async changeName(userName) {
        const res = await api.post('/api/changeName', {
            user_name: userName
        });
        return res.data
    },

    async changeEmail(userEmail, password) {
        const res = await api.post('api/changeEmail', {
            user_email: userEmail,
            password: password
        });
        return res.data
    },

    async sendEmail(recipientId, recipientEmail, mainText, emailTitle ) {
        const res = await api.post('/api/sendEmail', {
            email_text: mainText,
            email_title: emailTitle,
            recipient_id: recipientId ?? null,
            recipient_email: recipientEmail ?? null
        });
        return res.data
    }
}

export function disposeReturn(data) {

    if (data.error) {
        showTips(data.error);
        return true;
    }
    if (data.xp_change) {
        userModule.changeXp(data.xp_change)
    }
    if (data.msg) {
        showTips(data.msg);
        return false;
    }
    return false;
}