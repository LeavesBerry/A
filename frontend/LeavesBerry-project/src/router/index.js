// src/router/index.js
import axios from 'axios';
import { createRouter, createWebHistory } from 'vue-router'
import { pageState } from '../utils/index.js'

const pageModules = import.meta.glob('../pages/*.vue')

export const ROOTPATH = window.location.origin
export const SERVERPATH = "http://localhost:5000"

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
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach(async (to, from, next) => {
    const needLoginPages = ['Test2'];
    if (needLoginPages.includes(to.name)) {
        try {
            const res = await axios.get('/api/getUserInfo');
            next();
        } catch (err) {
            next(false);
        }
    }
    else {
        next();
    }
});



export default router;