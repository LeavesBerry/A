import { watch } from "vue";
import { useRoute } from "vue-router";
import router from "../router";
import { configModule } from "./config";
import { pageState, updatePageInfo } from "./page";
import { userState } from "./user";
import { apiRequest, disposeReturn } from "./request";
import { navbarModule } from "./navbar";

export let visitList = [];
let timer = null;

async function submitVisitList() {
    console.log(1)
    if (!userState.isLogined || visitList.length == 0) return
    try {
        const res = await apiRequest.submitVisitList(visitList)
        if (!disposeReturn(res)) {
            visitList = []
        }
    }
    catch (e) {
        console.log(e)
    }
}

export function startTimer() {
    if (timer) clearInterval(timer)
    timer = setInterval(() => {
        submitVisitList()
    }, 60000)

}

let isRouteWithConfig = false

export function routeListener() {
    const route = useRoute();
    watch(
        () => route.fullPath,
        (newPath) => {
            if (isRouteWithConfig) {
                isRouteWithConfig = false
                return
            }
            else {
                updatePageInfo(route.params.page, `${newPath}`)
                navbarModule.initColl();
            }

        },
        { flush: "sync", immediate: true }
    )
}

export function useGoPage() {

    function goPage(url) {
       
        const reg = /^(.*)\/([^\/]+)\/config_index:(\d+)$/;
        const matchResult = url.match(reg)
        if (!matchResult) {
            router.push(url)
            return true
        }
        else {
            isRouteWithConfig = true
            const folderName = matchResult[2];
            const baseUrl = matchResult[1] + "/" + folderName;
            const configNum = Number(matchResult[3]);
            try {
                router.push(baseUrl)
                configModule.expandContent(configNum, folderName,
                    `${baseUrl}`)
                if (url !== visitList[-1]) {
                    visitList.push({url: pageState.currentUrl, title: pageState.currentTitle, 
                        type: pageState.currentType, desc: pageState.currentDesc})
                }

                return true
            } catch {
                return false
            }

        }

    }

    function backPage() {
        router.back()
    }

    function goPageByName(routeName, parmes) {
        router.push({ name: routeName, parmes: parmes })
    }

    return { goPage, backPage, goPageByName }
}
