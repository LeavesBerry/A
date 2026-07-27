<template>
    <div class="page" id="setting-page">
        <div class="slide-page">
            <input v-model="bioInputValue">
            <input type="file" accept="image/*" @change="selectAvatarFile($event)">

            <button @click="changeAvatar" :disabled="!cropReady">
                上传头像
            </button>

            <div v-if="originImgUrl" id="preview-box" ref="previewRef">

                <img :src="originImgUrl" ref="imgRef" id="origin-img" draggable="false" @load="initCropBox">

                <div id="crop-box" :style="cropBoxStyle" @mousedown="startMove">

                    <div v-for="handle in handles" :key="handle" :class="['handle', handle]"
                        @mousedown.stop="startResize(handle, $event)">
                    </div>

                </div>
            </div>
        </div>

        <teleport class="fixed-page" to="#app #app-root">
            <Logo></Logo>
        </teleport>
    </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import Logo from '../components/Logo.vue'
import { SERVERPATH } from '../router/index.js'
import { apiRequest, userState, disposeReturn } from '../utils/index.js'

const bioInputValue = ref(userState.bio)

const avatarFlie = ref(null)
const originImgUrl = ref('')
const imgRef = ref(null)
const previewRef = ref(null)

const TARGET_CROP_WIDTH = 300
const TARGET_CROP_HEIGHT = 300

const crop = ref({ x: 80, y: 50, size: 200 })

const scaleRatioX = ref(1)
const scaleRatioY = ref(1)

const dragging = ref(false)
const resizing = ref(false)
const resizeDirection = ref('')

const startPoint = ref({ x: 0, y: 0 })
const startCrop = ref({ x: 0, y: 0, size: 0 })
const handles = ['lt', 'rt', 'lb', 'rb', 'top', 'bottom', 'left', 'right']

const cropReady = computed(() => {
    return originImgUrl.value && crop.value.size > 0
})


const cropBoxStyle = computed(() => {
    return {
        left: crop.value.x + 'px',
        top: crop.value.y + 'px',
        width: crop.value.size + 'px',
        height: crop.value.size + 'px'
    }
})


function initCropBox() {
    const img = imgRef.value
    if (!img) return

    scaleRatioX.value = img.naturalWidth / img.clientWidth
    scaleRatioY.value = img.naturalHeight / img.clientHeight

    const size = Math.min(img.clientWidth, img.clientHeight) * 0.6
    crop.value = { x: (img.clientWidth - size) / 2, y: (img.clientHeight - size) / 2, size }
}


function limitCrop(next) {
    const img = imgRef.value

    if (!img) return next

    next.size = Math.max(40, Math.min(next.size, img.clientWidth, img.clientHeight))
    next.x = Math.max(0, Math.min(next.x, img.clientWidth - next.size))
    next.y = Math.max(0, Math.min(next.y, img.clientHeight - next.size))

    return next
}


function startMove(e) {
    dragging.value = true
    startPoint.value = { x: e.clientX, y: e.clientY }
    startCrop.value = { ...crop.value }

    window.addEventListener('mousemove', moveCrop)
    window.addEventListener('mouseup', stopAction)
}


function moveCrop(e) {
    if (!dragging.value && !resizing.value) return

    const dx = e.clientX - startPoint.value.x
    const dy = e.clientY - startPoint.value.y

    if (dragging.value) {
        crop.value = limitCrop({
            ...startCrop.value, x: startCrop.value.x + dx,
            y: startCrop.value.y + dy
        })
    }
    else {
        resizeCrop(dx, dy)
    }
}


function startResize(direction, e) {
    resizing.value = true
    resizeDirection.value = direction
    startPoint.value = { x: e.clientX, y: e.clientY }
    startCrop.value = { ...crop.value }

    window.addEventListener('mousemove', moveCrop)
    window.addEventListener('mouseup', stopAction)
}


function resizeCrop(dx, dy) {
    const old = startCrop.value
    let size = old.size
    let x = old.x
    let y = old.y

    const direction = resizeDirection.value

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
    if (size < minSize)
        size = minSize
    if (direction.includes('l'))
        x = old.x + old.size - size
    if (direction.includes('t'))
        y = old.y + old.size - size

    crop.value = limitCrop({ x, y, size })
}


function stopAction() {
    dragging.value = false
    resizing.value = false

    window.removeEventListener('mousemove', moveCrop)
    window.removeEventListener('mouseup', stopAction)
}


function selectAvatarFile(e) {
    const file = e.target.files[0]
    if (!file || !file.type.startsWith('image/')) return

    avatarFlie.value = file

    if (originImgUrl.value) URL.revokeObjectURL(originImgUrl.value)
    originImgUrl.value = URL.createObjectURL(file)
}



function getCropBlob() {
    const canvas = document.createElement('canvas')
    canvas.width = TARGET_CROP_WIDTH
    canvas.height = TARGET_CROP_HEIGHT
    const ctx = canvas.getContext('2d')
    const img = imgRef.value
    const sx = crop.value.x * scaleRatioX.value
    const sy = crop.value.y * scaleRatioY.value
    const size = crop.value.size

    ctx.drawImage(img, sx, sy, size * scaleRatioX.value, size * scaleRatioY.value,
        0, 0, TARGET_CROP_WIDTH, TARGET_CROP_HEIGHT)

    return new Promise(resolve => {
        canvas.toBlob(resolve, 'image/jpeg', 0.85)
    })
}


async function changeAvatar() {
    if (!userState.isLogined)
        return

    const blob = await getCropBlob()
    const res = await apiRequest.changeAvatar(blob)

    if (!disposeReturn(res)) {
        userState.avatarUrl = res.avatar_url
    }
}

onUnmounted(() => {
    stopAction()
    if (originImgUrl.value)
        URL.revokeObjectURL(originImgUrl.value)

})
</script>

<style scoped>
#preview-box {
    position: relative;
    width: 600px;
    overflow: hidden;

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
</style>
