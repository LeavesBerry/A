import { ref, reactive } from "vue";
import { pageState, updatePageInfo } from "./page";
import api from "./api";
import { navbarModule } from "./navbar"
import router from "../router";
import { apiRequest } from "./request";


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

    async expandContent(id, field, url = pageState.currentUrl) {
        pageState.currentUrl = url + `/config_index:${id}`
        navbarModule.initColl()
        if (this.contentId !== id) {
            const res = await api.post(`/api/get${field}Content`, { id: id });
            pageState.currentTitle = res.data.title;
            pageState.currentDesc = res.data.desc;
            pageState.currentType = fieldTypeConfig[field] ?? "other";
            this.contentText = res.data.main_text;
            this.contentTitle = res.data.title;
            this.contentId = id;
        }
        else {
            pageState.currentTitle = `${this.contentId}号公告`;
            pageState.currentDesc = `${this.contentTitle}`
            pageState.currentType = "essay"
        }
        
        this.isConfigClosed = true
        this.isContentExpanded = true
        if(pageState.isCollected) {
            await apiRequest.refreshColl(pageState.currentUrl,
                pageState.currentTitle, pageState.currentType, 
                pageState.currentDesc)
        }
    },

    hideContent() {
        const route = router.currentRoute.value
        updatePageInfo(route.params.page, location.href);
        navbarModule.initColl();
        this.isContentExpanded = false;
        setTimeout(() => {
            this.isConfigClosed = false
        }, 400);
    }
})
