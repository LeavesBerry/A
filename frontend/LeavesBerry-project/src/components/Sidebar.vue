<template>
    <div class="sidebar">
        <div class="sidebar-config" v-for="item in typeList" :key="item.index" 
            :id="'sidebar-' + item.id" :class="{ activediv: currentSidebarConfig === item.index }"
            @click="handleItemClick(item.index, item.typeKey)">
            <span class="sidebar-config-text"
            :class="{ activespan: currentSidebarConfig === item.index }">❖{{ item.label }}❖</span>
        </div>
    </div>

</template>
<script setup>
import { currentSidebarConfig, configModule } from '../utils/index';
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
        currentSidebarConfig.value = sn;
        emit("changeDir", sn, type)
    }

}
</script>

<style scoped>
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

.sidebar-config {
    width: 23vw;
    height: calc(8 * var(--design-vh, 4.57px));
    background-color: #FFF3D0;
    border-top: 1px solid #180f0b;
    border-bottom: 1px solid #180f0b;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: calc(2 * var(--design-vh, 4.57px));
    margin-left: 1vw;
    transition: all 0.3s ease;
}

.sidebar-config-text {
    color: #180f0b;
    font-size: calc(3.5 * var(--design-vh, 4.57px));
    font-weight: 500;
    letter-spacing: 10px;
    transition: all 0.3s ease;
}

.activespan{
    color: #5A191B;
    transform: scale(1.15);
}

.activediv {
    padding-left: 1vw;
    border-color: #5A191B;
}
</style>