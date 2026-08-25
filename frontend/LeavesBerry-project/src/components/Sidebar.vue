<template>
    <div class="sidebar">
        <button class="sidebar-config" v-for="item in typeList" :key="item.index" 
            :id="'sidebar-' + item.id" :class="{ activediv: currentSidebarConfig === item.index }"
            @click="handleItemClick(item.index, item.typeKey)">
            <span class="sidebar-config-text"
            :class="{ activespan: currentSidebarConfig === item.index }">❖{{ item.label }}❖</span>
        </button>
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
    top: var(--navbar-height);
    background-color: var(--primary-color);
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
    height: var(--navbar-height);
    background-color: var(--primary-color);
    border: 1px solid var(--secondary-color);
    border-radius: calc(3 * var(--design-vh, 4.57px));
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: calc(2 * var(--design-vh, 4.57px));
    margin-left: 1vw;
}

.sidebar-config-text {
    color: var(--secondary-color);
    font-size: calc(3.5 * var(--design-vh, 4.57px));
    font-weight: 500;
    letter-spacing: 10px;
    transition: color 0.3s ease;
}

.activespan{
    color: var(--primary-color);
}

.activediv {
    background-color: var(--secondary-color);
}

@media (min-width: 1px) and (orientation: portrait) {
	.sidebar-config-text {
        font-size: calc(2.7 * var(--design-vh, 4.57px));
        letter-spacing: 2.5px;
    }
}
</style>