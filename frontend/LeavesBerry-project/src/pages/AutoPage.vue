<template>
    <component :is="currentComponent" v-if="currentComponent"></component>
    <div v-else>
        <p id="no-page-tip">{{ "抱歉,您所访问的界面不存在:(" }}</p>
    </div>
</template>

<script>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { getPreloadedPageComponent } from '../router';

export default {
    setup() {
        const route = useRoute();

        const currentComponent = computed(() => {
            const pageName = route.params.page;
            return getPreloadedPageComponent(pageName);
        });

        return { currentComponent };
    }
}
</script>

<style scoped>
#no-page-tip {
    margin-top: calc(50vh - 52px);
    font-size: 20px;
    font-weight: 300;
    color: var(--secondary-color);
}
</style>
