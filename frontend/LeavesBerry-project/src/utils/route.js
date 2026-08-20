import { nextTick, watch } from "vue";
import { useRoute } from "vue-router";
import router, { preloadPageComponent } from "../router";
import { configModule } from "./config";
import { pageState, updatePageInfo } from "./page";
import { userState } from "./user";
import { apiRequest } from "./request";
import { navbarModule } from "./navbar";

export let visitList = [];
let timer = null;

async function submitVisitList() {
    if (!userState.isLogined || visitList.length == 0) return;
    try {
        await apiRequest.submitVisitList(visitList);
        visitList = [];
    }
    catch (e) {
        console.log(e);
    }
}

export function startTimer() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => {
        submitVisitList();
    }, 60000);
}

let isRouteWithConfig = false;

export function routeListener() {
    const route = useRoute();
    watch(
        () => route.fullPath,
        (newPath) => {
            if (isRouteWithConfig) {
                isRouteWithConfig = false;
                return;
            }
            else {
                updatePageInfo(route.params.page, `${newPath}`);
                navbarModule.initColl();
            }
        },
        { flush: "sync", immediate: true }
    );
}

/**
 * 在 router.push() 之前把目标 /:page 页面组件加载完成。
 * 这里只等待组件 chunk，不等待页面里的 API、图片等资源。
 */
async function prepareTargetPage(target) {
    const resolved = router.resolve(target);

    if (resolved.name === "AutoPage") {
        await preloadPageComponent(resolved.params.page);
    }
}

export function useGoPage() {

    async function goPage(url) {
        const reg = /^(.*)\/([^\/]+)\/config_index:(\d+)$/;
        const matchResult = url.match(reg);

        if (!matchResult) {
            try {
                // 1. 旧页面保持显示，先下载并解析目标页面组件
                await prepareTargetPage(url);

                // 2. 目标组件 ready 后才真正改变路由
                await router.push(url);

                // 3. 等待 Vue 完成本轮 DOM patch。
                //    此时 transition 中的新节点已经包含目标页面 DOM。
                await nextTick();

                if (url !== visitList.at(-1)) {
                    visitList.push({
                        url: pageState.currentUrl,
                        title: pageState.currentTitle,
                        type: pageState.currentType,
                        desc: pageState.currentDesc
                    });
                }

                return true;
            } catch (e) {
                console.error("Navigation failed:", e);
                return false;
            }
        }
        else {
            const folderName = matchResult[2];
            const baseUrl = matchResult[1] + "/" + folderName;
            const configNum = Number(matchResult[3]);

            try {
                // config 跳转同样先把真正页面组件准备好
                await prepareTargetPage(baseUrl);

                isRouteWithConfig = true;

                // 页面组件 ready 后再切换路由
                await router.push(baseUrl);

                // expandContent 可能需要查询/操作新页面 DOM，
                // 所以必须等 Vue 把新页面 patch 到 DOM 后再执行。
                await nextTick();

                configModule.expandContent(
                    configNum,
                    folderName,
                    `${baseUrl}`
                );

                if (url !== visitList.at(-1)) {
                    visitList.push({
                        url: pageState.currentUrl,
                        title: pageState.currentTitle,
                        type: pageState.currentType,
                        desc: pageState.currentDesc
                    });
                }

                return true;
            } catch (e) {
                isRouteWithConfig = false;
                console.error("Navigation with config failed:", e);
                return false;
            }
        }
    }

    function backPage() {
        router.back();
    }

    async function goPageByName(routeName, params) {
        try {
            const target = { name: routeName, params };

            await prepareTargetPage(target);
            await router.push(target);
            await nextTick();

            return true;
        } catch (e) {
            console.error("Navigation by name failed:", e);
            return false;
        }
    }

    return { goPage, backPage, goPageByName };
}
