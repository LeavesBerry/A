// src/router/index.js
import axios from 'axios';
import { createRouter, createWebHistory } from 'vue-router';

const pageModules = import.meta.glob('../pages/*.vue');

// 已经完成 import 的真实页面组件缓存。

const preloadedPageComponents = new Map();

export const ROOTPATH = window.location.origin;
export const SERVERPATH = "http://localhost:5000";

/**
 * 预加载 /:page 对应的真实页面组件。
 */
export async function preloadPageComponent(pageName) {
    if (!pageName || typeof pageName !== 'string') {
        return null;
    }

    if (preloadedPageComponents.has(pageName)) {
        return preloadedPageComponents.get(pageName);
    }

    const componentPath = `../pages/${pageName}.vue`;
    const loader = pageModules[componentPath];

    if (!loader) {
        return null;
    }

    const module = await loader();
    const component = module.default;

    preloadedPageComponents.set(pageName, component);
    return component;
}

/**
 * 给 AutoPage.vue 同步读取已经预加载好的组件。
 */
export function getPreloadedPageComponent(pageName) {
    return preloadedPageComponents.get(pageName) ?? null;
}

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('../pages/Home.vue'), // 初始界面
        meta: {
            title: '主页',
            type: 'other',
            description: '本站的开始界面'
        }
    },
    {
        path: '/:page',
        name: 'AutoPage',
        component: () => import('../pages/AutoPage.vue'),
        meta: {
            title: '未知界面',
            type: 'other',
            description: '未在本站详细注册的页面'
        }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

/**
 * 无论导航来自：
 * - goPage()
 * - 浏览器前进 / 后退
 * - 地址栏直接访问
 * 都先把 /:page 对应的真实页面组件加载完成，再确认路由切换。
 */
router.beforeEach(async (to, from, next) => {
    try {
        if (to.name === 'AutoPage') {
            await preloadPageComponent(to.params.page);
        }

        const needLoginPages = ['Test2'];

        if (needLoginPages.includes(to.name)) {
            try {
                await axios.get('/api/getUserInfo');
                next();
            } catch (err) {
                next(false);
            }
        } else {
            next();
        }
    } catch (err) {
        console.error('Failed to preload target page:', err);
        next(false);
    }
});

export default router;
