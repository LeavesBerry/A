<template>
    <div class="page" id="setting-page">
        <div class="slide-page">
            <div class="item-box" v-if="currentContent == 'name'">
                <input class="item" id="name-input" v-model="nameInputValue" placeholder="请输入名称 | 8字以内"
                maxlength="8">
                <button class="item" id="change-name-button" @click="changeName">更改名称</button>
            </div>
            <div class="item-box" v-if="currentContent == 'bio'">
                <input class="item" id="bio-input" v-model="bioInputValue" placeholder="请输入简介 | 26字以内"
                maxlength="26">
                <button class="item" id="change-bio-button" @click="bioModule.changeBio">更改简介</button>
                <p class="refresh-tip">•如果你想不出一个满意的简介,不妨试试</p>
                <div style="width: 70vw;position:absolute;top: 60%;border-top: 3px solid #3a251a;"></div>
                <div id="gener-bio-button-box">
                    <button class="gener-bio-button item" id="poem-gener-bio-button"
                    @click="bioModule.generBio('poetry')">从诗歌中选取</button>
                    <button class="gener-bio-button item" id="game-gener-bio-button"
                    @click="bioModule.generBio('lines')">从台词中选取</button>
                </div>
            </div>
            <div class="item-box" v-if="currentContent == 'avatar'">
                <label class="item" id="avatar-input">
                    <span id="docu-name">
                        {{ avatarState.avatarFile ? `已选择: ${avatarState.avatarFile.name} | 点击更改` : "点击选择文件" }}
                    </span>
                    <input placeholder="选择文件" type="file" accept="image/*" @change="avatarModule.selectFile($event)">
                </label>

                <button class="item" id="change-avatar-button" @click="avatarModule.changeAvatar"
                    :disabled="!avatarModule.cropReady">更改头像</button>

                <div id="crop-area">
                    <div id="crop-tip-box">
                        <p id="crop-tip" v-for="(item, index) in avatarState.tipList" :key="`${item}-${index}`"
                        v-if="avatarState.avatarFile">•{{ item }}</p>
                    </div>

                    <div v-if="avatarState.originImgUrl" id="preview-box" :ref="el => avatarState.previewRef = el">
                        <img :src="avatarState.originImgUrl" :ref="el => avatarState.imgRef = el" id="origin-img" draggable="false" @load="avatarModule.initCropBox">
                        <div id="crop-box" :style="avatarModule.cropBoxStyle" @mousedown="avatarModule.startMove">
                            <div v-for="handle in avatarState.handles" :key="handle" :class="['handle', handle]"
                                @mousedown.stop="avatarModule.startResize(handle, $event)">
                            </div>
                        </div>
                    </div>
                </div>

                <div class="space"></div>

            </div>
            <div class="item-box" v-if="currentContent == 'email'">
                <input class="item" id="email-input" v-model="emailInputValue" placeholder="请输入邮箱"
                maxlength="40">
                <input class="item" id="password-input" v-model="passwordInputValue" placeholder="请输入密码"
                maxlength="40">
                <button class="item" id="change-email-button" @click="changeEmail">更改邮箱</button>
            </div>
            <div class="item-box" v-if="currentContent == 'logout'"></div>
        </div>
        <teleport class="fixed-page" to="#app #app-root">
            <Logo></Logo>
            <Sidebar :type-list="setTypeList" @change-dir="switchDirContent"></Sidebar>
        </teleport>
    </div>
</template>

<script setup>
import { ref, reactive, onUnmounted, onMounted } from 'vue'
import Logo from '../components/Logo.vue'
import Sidebar from '../components/Sidebar.vue'
import {
    apiRequest, userState, disposeReturn, showTips, currentSidebarConfig,
    updatePersistFields, persistConfig
} from '../utils/index.js'

const setTypeList = [
    { index: 0, typeKey: "name", label: "名称", id: "name" },
    { index: 1, typeKey: "bio", label: "简介", id: "bio" },
    { index: 2, typeKey: "avatar", label: "头像", id: "avatar" },
    { index: 3, typeKey: "email", label: "邮箱", id: "email" },
    { index: 4, typeKey: "logout", label: "注销", id: "logout" }
]
const currentContent = ref('')

// ------------------------------
// 头像处理
// ------------------------------
const avatarState = reactive({
    avatarFile: null,
    originImgUrl: '',
    imgRef: null,
    previewRef: null,
    tipList: [
        "用红色裁剪框框选你希望设置为头像的部分",
        "最终头像框展示你所选择的部分的内切圆内的图像"
    ],
    TARGET_CROP_WIDTH: 300,
    TARGET_CROP_HEIGHT: 300,
    crop: { x: 80, y: 50, size: 200 },
    scaleRatioX: 1,
    scaleRatioY: 1,
    dragging: false,
    resizing: false,
    resizeDirection: '',
    startPoint: { x: 0, y: 0 },
    startCrop: { x: 0, y: 0, size: 0 },
    handles: ['lt', 'rt', 'lb', 'rb', 'top', 'bottom', 'left', 'right']
})

const avatarModule = {
    get cropReady() {
        return Boolean(avatarState.originImgUrl && avatarState.crop.size > 0)
    },

    get cropBoxStyle() {
        return {
            left: avatarState.crop.x + 'px',
            top: avatarState.crop.y + 'px',
            width: avatarState.crop.size + 'px',
            height: avatarState.crop.size + 'px'
        }
    },

    initCropBox() {
        const img = avatarState.imgRef
        if (!img) return

        avatarState.scaleRatioX = img.naturalWidth / img.clientWidth
        avatarState.scaleRatioY = img.naturalHeight / img.clientHeight

        const size = Math.min(img.clientWidth, img.clientHeight) * 0.6
        avatarState.crop = {
            x: (img.clientWidth - size) / 2,
            y: (img.clientHeight - size) / 2,
            size
        }
    },

    limitCrop(next) {
        const img = avatarState.imgRef
        if (!img) return next

        next.size = Math.max(40, Math.min(next.size, img.clientWidth, img.clientHeight))
        next.x = Math.max(0, Math.min(next.x, img.clientWidth - next.size))
        next.y = Math.max(0, Math.min(next.y, img.clientHeight - next.size))

        return next
    },

    startMove(e) {
        avatarState.dragging = true
        avatarState.startPoint = { x: e.clientX, y: e.clientY }
        avatarState.startCrop = { ...avatarState.crop }

        window.addEventListener('mousemove', avatarModule.moveCrop)
        window.addEventListener('mouseup', avatarModule.stopAction)
    },

    moveCrop(e) {
        if (!avatarState.dragging && !avatarState.resizing) return

        const dx = e.clientX - avatarState.startPoint.x
        const dy = e.clientY - avatarState.startPoint.y

        if (avatarState.dragging) {
            avatarState.crop = avatarModule.limitCrop({
                ...avatarState.startCrop,
                x: avatarState.startCrop.x + dx,
                y: avatarState.startCrop.y + dy
            })
        } else {
            avatarModule.resizeCrop(dx, dy)
        }
    },

    startResize(direction, e) {
        avatarState.resizing = true
        avatarState.resizeDirection = direction
        avatarState.startPoint = { x: e.clientX, y: e.clientY }
        avatarState.startCrop = { ...avatarState.crop }

        window.addEventListener('mousemove', avatarModule.moveCrop)
        window.addEventListener('mouseup', avatarModule.stopAction)
    },

    resizeCrop(dx, dy) {
        const old = avatarState.startCrop
        let size = old.size
        let x = old.x
        let y = old.y

        const direction = avatarState.resizeDirection

        if (direction.includes('r')) {
            size = old.size + dx
        }
        if (direction.includes('b')) {
            size = old.size + dy
        }
        if (direction.includes('l')) {
            size = old.size - dx
            x = old.x + dx
        }
        if (direction.includes('t')) {
            size = old.size - dy
            y = old.y + dy
        }

        const minSize = 40
        if (size < minSize) {
            size = minSize
        }
        if (direction.includes('l')) {
            x = old.x + old.size - size
        }
        if (direction.includes('t')) {
            y = old.y + old.size - size
        }

        avatarState.crop = avatarModule.limitCrop({ x, y, size })
    },

    stopAction() {
        avatarState.dragging = false
        avatarState.resizing = false

        window.removeEventListener('mousemove', avatarModule.moveCrop)
        window.removeEventListener('mouseup', avatarModule.stopAction)
    },

    selectFile(e) {
        const file = e.target.files?.[0]
        if (!file || !file.type.startsWith('image/')) return

        avatarState.avatarFile = file
        avatarModule.revokeOriginImgUrl()
        avatarState.originImgUrl = URL.createObjectURL(file)
    },

    revokeOriginImgUrl() {
        if (!avatarState.originImgUrl) return

        URL.revokeObjectURL(avatarState.originImgUrl)
        avatarState.originImgUrl = ''
    },

    getCropBlob() {
        const img = avatarState.imgRef
        if (!img) {
            return Promise.resolve(null)
        }

        const canvas = document.createElement('canvas')
        canvas.width = avatarState.TARGET_CROP_WIDTH
        canvas.height = avatarState.TARGET_CROP_HEIGHT

        const ctx = canvas.getContext('2d')
        if (!ctx) {
            return Promise.resolve(null)
        }

        const sx = avatarState.crop.x * avatarState.scaleRatioX
        const sy = avatarState.crop.y * avatarState.scaleRatioY
        const sourceWidth = avatarState.crop.size * avatarState.scaleRatioX
        const sourceHeight = avatarState.crop.size * avatarState.scaleRatioY

        ctx.drawImage(
            img,
            sx,
            sy,
            sourceWidth,
            sourceHeight,
            0,
            0,
            avatarState.TARGET_CROP_WIDTH,
            avatarState.TARGET_CROP_HEIGHT
        )

        return new Promise(resolve => {
            canvas.toBlob(resolve, 'image/jpeg', 0.85)
        })
    },

    async changeAvatar() {
        if (!userState.isLogined || !avatarModule.cropReady) return

        const blob = await avatarModule.getCropBlob()
        if (!blob) {
            showTips("头像裁剪失败，请重新选择图片")
            return
        }

        const res = await apiRequest.changeAvatar(blob)
        if (!disposeReturn(res)) {
            const updateRes = updatePersistFields(userState, { avatarUrl: res.avatar_url }, persistConfig)
            if (updateRes.skipped) {
                console.warn(updateRes.skipped)
            }
        }
    },

    dispose() {
        avatarModule.stopAction()
        avatarModule.revokeOriginImgUrl()
        avatarState.avatarFile = null
        avatarState.imgRef = null
        avatarState.previewRef = null
    }
}

// ------------------------------
// 简介处理
// ------------------------------
const bioInputValue = ref(userState.bio)

const bioModule = {
    async changeBio() {
        if (!userState.isLogined || !bioInputValue.value) return
        if (bioInputValue.value.length > 26) {
            showTips("简介字数需在26字以内")
            return
        }
        
        const reg = /((https?|ftp|file):\/\/)?(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z0-9\-]+|(?:\d{1,3}\.){3}\d{1,3}(?:\/[\w.,@?^=%&:/~+#\-]*)*/g

        if (reg.test(bioInputValue.value)) {
            showTips("简介中禁止包含链接!")
            return
        }

        const res = await apiRequest.changeBio(bioInputValue.value)
        if (!disposeReturn(res)) {
            const updateRes = updatePersistFields(userState, { bio: bioInputValue.value }, persistConfig)
            if (updateRes.skipped.length > 0) {
                console.warn(updateRes.skipped)
            }
        }
    },

    async generBio(type) {
        let selectedJsonIndex = null
        switch (type) {
            case "poetry":
                selectedJsonIndex = Math.floor(Math.random() * 5)
                break;
            case "lines":
                selectedJsonIndex = Math.floor(Math.random() * 2)    
                break;
        }

        const cache = localStorage.getItem(`${type}_cache_${selectedJsonIndex}`)
        let bioList = []
        if (cache) {
            bioList = JSON.parse(cache)
        }
        else {
            const bios = await fetch(`/text/${type}/${type}_${selectedJsonIndex}.json`)
            bioList = await bios.json()
            localStorage.setItem(`${type}_cache_${selectedJsonIndex}`, JSON.stringify(bioList))
        }
        const index = Number(Math.floor(Math.random() * bioList.length))
        bioInputValue.value = bioList[index]
    },
}

// ------------------------------
// 名称处理
// ------------------------------
const nameInputValue = ref(userState.userName)
async function changeName() {
    if (!userState.isLogined || !nameInputValue.value) return
        if (nameInputValue.value.length > 10) {
            showTips("名称字数需在8字以内")
            return
        }

        const res = await apiRequest.changeName(nameInputValue.value)
        if (!disposeReturn(res)) {
            const updateRes = updatePersistFields(userState, { userName: nameInputValue.value }, persistConfig)
            if (updateRes.skipped.length > 0) {
                console.warn(updateRes.skipped)
            }
        }
}

// ------------------------------
// 邮箱处理
// ------------------------------
const emailInputValue = ref(userState.userEmail)
const passwordInputValue = ref(null)
async function changeEmail() {
    if (!userState.isLogined || !emailInputValue.value) return
        const reg = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        const match = emailInputValue.value.trim().match(reg)
        if (emailInputValue.value.length > 40 || !match) {
            showTips("邮箱格式错误")
            return
        }
        if (passwordInputValue.value.length > 40) {
            showTips("密码格式错误")
            return
        }
        const res = await apiRequest.changeEmail(emailInputValue.value, passwordInputValue.value)
        if (!disposeReturn(res)) {
            const updateRes = updatePersistFields(userState, { userEmail: emailInputValue.value }, persistConfig)
            if (updateRes.skipped.length > 0) {
                console.warn(updateRes.skipped)
            }
        }
}



function switchDirContent(sn, type) {
    currentSidebarConfig.value = sn
    currentContent.value = type ?? ""
}

onMounted(() => {
    currentSidebarConfig.value = 0
    currentContent.value = "name"
})

onUnmounted(() => {
    avatarModule.dispose()
})
</script>

<style scoped>
#crop-area {
    position: relative;
    top: calc(8 * var(--design-vh));
}

#preview-box {
    position: absolute;
    width: 600px;
    overflow: hidden;
    top: 0;
    left: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    border: 3px solid #3a251a;
}

#crop-tip-box {
    position: absolute;
    top: -4px;
    left: 620px;
    width: calc(70vw - 620px);
    text-align: left;
}

#crop-tip {
    white-space: pre-line;
    word-break: break-all;
    word-wrap: break-word;
    color: #3a251a;
    font-size: 16px;
    font-weight: 200;
}

#origin-img {
    width: 100%;
    display: block;
    user-select: none;
}


#crop-box {
    position: absolute;
    border: 2px solid red;
    box-sizing: border-box;
    cursor: move;
}


.handle {
    position: absolute;
    width: 12px;
    height: 12px;
    background: white;
    border: 2px solid red;
    box-sizing: border-box;
}


.lt {
    left: -6px;
    top: -6px;
    cursor: nw-resize;
}

.rt {
    right: -6px;
    top: -6px;
    cursor: ne-resize;
}

.lb {
    left: -6px;
    bottom: -6px;
    cursor: sw-resize;
}

.rb {
    right: -6px;
    bottom: -6px;
    cursor: se-resize;
}


.top {
    left: 50%;
    top: -6px;
    cursor: n-resize;
}

.bottom {
    left: 50%;
    bottom: -6px;
    cursor: s-resize;
}

.left {
    left: -6px;
    top: 50%;
    cursor: w-resize;
}

.right {
    right: -6px;
    top: 50%;
    cursor: e-resize;
}

#avatar-input {
    height: calc(8 * var(--design-vh));
    flex-direction: column;
    text-align: center;
}

#avatar-input::placeholder {
    text-align: center;
}

#avatar-input input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
}

#docu-name {
    font-size: 20px;
    color: #3a251a;
    font-weight: 600;
}

.item {
    height: calc(8 * var(--design-vh));
    flex-direction: column;
    padding-top: calc(0.4 * var(--design-vh));
    text-align: center;
    font-size: 20px;
    color: #3a251a;
    font-weight: 600;
    outline: none;
    border: none;
    line-height: calc(8 * var(--design-vh));
    display: flex;
    align-items: center;
    justify-content: center;
}

.space {
    margin-top: 80vh;
    width: 100vw;
    height: 10vh;
    background:none;
}

</style>
