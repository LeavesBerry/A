<template>
    <component :is="currentComponent" v-if="currentComponent"></component>
    <div v-else>
        <p id="no-page-tip">{{ "抱歉,您所访问的界面不存在:(" }}</p>
    </div>
</template>
<script>
import { defineAsyncComponent, computed } from 'vue';
import { useRoute } from 'vue-router';
export default {
    setup() {
        const route = useRoute();
        const pageModules = import.meta.glob('./*.vue')
        const currentComponent = computed(() => {
            const pageName = route.params.page;
            const componentPath = `./${pageName}.vue`;
            if (pageModules[componentPath]) {
                return defineAsyncComponent(pageModules[componentPath]);
            }
            return null;
        });
        return { currentComponent }
    }
}
</script>

<style scoped>
#no-page-tip {
    margin-top: calc(50vh - 52px);
    font-size: 20px;
    font-weight: 300;
    color: #3a251a;
}
</style>