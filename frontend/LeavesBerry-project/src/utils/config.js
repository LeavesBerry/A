import { reactive } from "vue";
import { pageState } from "./page";
import api from "./api";
import { navbarModule } from "./navbar"
import { apiRequest } from "./request";
import { visitList } from "./route";
import router from "../router";


const fieldTypeConfig = {
    "Email": "essay",
    "Announce": "essay",
    "Music": "music"
}

export const configModule = reactive({
    isContentExpanded: false,
    isConfigClosed: false,
    contentTitle: "",
    contentText: "",
    contentId: null,

    expandContainer() {
        this.isConfigClosed = true
        this.isContentExpanded = true
        
    },

    async refreshColl() {
        if(pageState.isCollected) {
            await apiRequest.refreshColl(pageState.currentUrl,
                pageState.currentTitle, pageState.currentType, 
                pageState.currentDesc)
        }
    },

    async hideContent() {
        this.isContentExpanded = false;
        setTimeout(() => {
            this.isConfigClosed = false
        }, 400);
        await router.replace({
            hash: ''
        })
        navbarModule.initColl();
        
    },

    async expandContent(id, field) {  
        this.expandContainer()
        await router.push({
            hash: `#?config_index=${id}`
        })
        if (this.contentId !== id) {
            let contentCache = sessionStorage.getItem(`${field}_content_cache_${id}`)
            if (!contentCache) {
                const res = await api.post(`/api/get${field}Content`, { id: id });
                this.contentText = res.data.main_text;
                this.contentTitle = res.data.title;
                this.contentId = id;
                pageState.currentTitle = res.data.title;
                pageState.currentDesc = res.data.desc;
                pageState.currentType = fieldTypeConfig[field] ?? "other";        
                
                sessionStorage.setItem(`${field}_content_cache_${id}`, 
                    JSON.stringify({
                        contentText: this.contentText,
                        contentTitle: this.contentTitle,
                        contentDesc: res.data.desc,
                        currentType: fieldTypeConfig[field] ?? "other"
                    }))
            }
            else {
                contentCache = JSON.parse(contentCache)
                this.contentText = contentCache.contentText
                this.contentTitle = contentCache.contentTitle;
                this.contentId = id;
                pageState.currentTitle = contentCache.currentTitle;
                pageState.currentDesc = contentCache.contentDesc;
                pageState.currentType = contentCache.currentType;
            }
        }
        else {
            pageState.currentTitle = this.currentTitle;
            pageState.currentDesc = this.currentDesc;
            pageState.currentType = this.currentType;
        }
        await this.refreshColl()
        if (url !== visitList.at(-1)) {
            visitList.push({
                url: pageState.currentUrl,
                title: pageState.currentTitle,
                type: pageState.currentType,
                desc: pageState.currentDesc
            });
        }
    },

    
})
