<template>
    <div class="sidebar">
        <span class="dir-active-arrow" :style="arrowStyle">{{ arrow }}</span>
        <div class="type" v-for="item in typeList" :key="item.index" :id="item.id"
            @click="handleItemClick(item.index, item.typeKey)">❖{{ item.label }}❖</div>
    </div>

</template>
<script setup>
import { arrowStyle, switchArrow, configModule } from '../utils/index';
const arrow = "<<<"
const props = defineProps({
    typeList: {
        type: Array,
        required: true,
        default: () => []
    }
})
const emit = defineEmits(["changeDir"])
function handleItemClick(sn, type) {
    if (!configModule.isContentExpanded) {
        switchArrow(sn)
        emit("changeDir", sn, type)
    }

}
</script>

<style>
.sidebar {
    width: 25vw;
    height: 100vh;
    position: fixed;
    top: calc(8 * var(--design-vh, 4.57px));
    background-color: #FFF3D0;
    left: 0;
    box-shadow: 0 10px 25px rgba(180, 145, 80, 1);
    z-index: 15;
}

.sidebar * {
    -webkit-user-select: none;
    user-select: none;
}

.type {
    width: 23vw;
    height: calc(8 * var(--design-vh, 4.57px));
    background-color: #FFF3D0;
    color: #3A251A;
    border-top: 1px solid #3A251A;
    border-bottom: 1px solid #3A251A;
    font-size: calc(3.5 * var(--design-vh, 4.57px));
    font-weight: 500;
    letter-spacing: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: calc(2 * var(--design-vh, 4.57px));
    margin-left: 1vw;
}

.dir-active-arrow {
    position: absolute;
    right: 15px;
    top: 15px;
    color: #3A251A;
    font-size: calc(3.5 * var(--design-vh, 4.57px));
    font-weight: 200;
    letter-spacing: 5px;
    transition: all 0.3s ease;
}
</style>