import { ref, reactive } from "vue";
import { pageState, updatePageInfo } from "./page";
import api from "./api";
import { navbarModule } from "./navbar"
import router from "../router";
import { apiRequest } from "./request";


export const configModule = reactive({
    isContentExpanded: false,
    isConfigClosed: false,
    contentTitle: "",
    contentText: "",
    contentId: null,

    async expandContent(id, type, url = pageState.currentUrl) {
        pageState.currentUrl = url + `/config_index:${id}`
        navbarModule.initColl()
        if (this.contentId !== id) {
            const res = await api.post(`/api/get${type}Text`, { id: id });
            pageState.currentTitle = res.data.title;
            this.contentText = res.data.main_text;
            this.contentTitle = res.data.title;
            this.contentId = id;
        }
        else {
            pageState.currentTitle = this.contentTitle;
        }
        pageState.currentType = "essay"
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
