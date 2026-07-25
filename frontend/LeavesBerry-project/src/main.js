import { createApp } from 'vue'
import { createHead } from '@vueuse/head'
import './style.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { api, refreshApi } from './utils/api.js'
import { userState, updatePersistFields, persistConfig } from './utils/index.js'

import './assets/base.css'
import './assets/navbar.css'
import './assets/login.css'
import './assets/menu.css'
import './assets/config.css'



const app = createApp(App)
const head = createHead()


api.interceptors.request.use(config => {
    const userToken = userState.userAccessToken;

    if (userToken && userToken !== 'visitor') {
        config.headers.Authorization = `Bearer ${userToken}`
    }

    return config
})

window.axios = axios

let isRefreshing = false;
let requestQueue = [];

api.interceptors.response.use(
    response => response,

    async error => {
        if (!error.response) {
            return Promise.reject(error);
        }

        const originalRequest = error.config;

        if (
            error.response.status !== 401 ||
            originalRequest._retry
        ) {
            return Promise.reject(error);
        }

        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                requestQueue.push({
                    resolve,
                    reject,
                    config: originalRequest
                });
            });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
            const result = await refreshApi.post(
                "/api/refreshToken"
            );

            const newAccessToken =
                result.data.access_token;

            updatePersistFields(
                userState,
                {
                    userAccessToken: newAccessToken
                },
                persistConfig
            );

            requestQueue.forEach(({ resolve, config }) => {
                config.headers.Authorization =
                    `Bearer ${newAccessToken}`;

                resolve(api(config));
            });

            requestQueue = [];

            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;

            return api(originalRequest);
        } catch (refreshError) {
            updatePersistFields(
                userState,
                {
                    userAccessToken: null,
                    isLogined: false
                },
                persistConfig
            );

            requestQueue.forEach(({ reject }) => {
                reject(refreshError);
            });

            requestQueue = [];

            return Promise.reject(refreshError);
        } finally {
            isRefreshing = false;
        }
    }
);


app.use(router)
app.config.globalProperties.$api = api
app.use(head)
app.mount('#app')
