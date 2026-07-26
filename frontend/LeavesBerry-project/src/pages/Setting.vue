<template>
    <div class="page" id="setting-page">
        <div class="slide-page"></div>
        <teleport class="fixed-page" to="#app #app-root">
            <Logo></Logo>
        </teleport>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import Logo from '../components/Logo.vue';
import { apiRequest, userState, showTips, disposeReturn } from '../utils/index.js';

let isUnmounted = false
let bioInputValue = ref(userState.bio)
let bioInputPlaceHolder = ref("请输入简介")
let avatarFlie = ref(null)

async function changeBio() {
    if (!userState.isLogined || bioInputValue.length == 0) return
    const res = await apiRequest.changeBio(bioInputValue.value)
    if (!disposeReturn(res)) {
        userState.bio = bioInputValue.value
    }
}

const selectAvatarFile = (e) => {
    const fileList = e.target.file
    if (fileList.length > 0) {
        avatarFlie.value = fileList[0]
    }
}

function changeAvatar() {
    if (!userState.isLogined || avatarFlie.length == 0) return
    const res = await apiRequest.changeAvatar(avatarFlie.value)
    if (!disposeReturn(res)) {
        userState.avatarUrl = res.avatar_url
    }
}

</script>