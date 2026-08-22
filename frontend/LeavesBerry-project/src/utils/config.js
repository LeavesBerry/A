import { ref, reactive } from "vue";
import { pageState, updatePageInfo } from "./page";
import api from "./api";
import { navbarModule } from "./navbar"
import { apiRequest } from "./request";
import { ROOTPATH } from "../router";
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

    hideContent() {
        const route = router.currentRoute.value
        updatePageInfo(route.params.page, location.href.replace(ROOTPATH, ''));
        navbarModule.initColl();
        this.isContentExpanded = false;
        setTimeout(() => {
            this.isConfigClosed = false
        }, 400);
    },

    async expandContent(id, field, url = pageState.currentUrl) {
        pageState.currentUrl = url + `/config_index:${id}`
        navbarModule.initColl()
        if (this.contentId !== id) {
            let contentCache = sessionStorage.getItem(`${field}_content_cache_${id}`)
            if (!contentCache) {
                const res = await api.post(`/api/get${field}Content`, { id: id });
                pageState.currentTitle = res.data.title;
                pageState.currentDesc = res.data.desc;
                pageState.currentType = fieldTypeConfig[field] ?? "other";
                this.contentText = res.data.main_text;
                this.contentTitle = res.data.title;
                this.contentId = id;
                this.expandContainer()
                await this.refreshColl()
                sessionStorage.setItem(`${field}_content_cache_${id}`, 
                    JSON.stringify({
                        contentText: this.contentText,
                        contentTitle: this.contentTitle
                    }))
                return
            }
            else {
                contentCache = JSON.parse(contentCache)
                this.contentText = cache.contentText
                this.contentTitle = cache.contentTitle;
                this.contentId = id;
            }
        }
        else {
            pageState.currentTitle = this.currentTitle;
            pageState.currentDesc = this.currentDesc;
            pageState.currentType = this.currentType;
        }
        this.expandContainer()
        await this.refreshColl()
    },

    
})
