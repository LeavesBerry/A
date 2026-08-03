<template>
	<div class="page" id="email-page">
		<div class="slide-page">
			<div class="item-box none-select" v-show="!configModule.isContentExpanded">
				<p class="no-item-tip none-select" v-if="currentConfig.length == 0" @click="getAllEmail">暂无邮件( •̀ ω
					•́
					)✧<br>点击此处刷新</p>
				<div class="item" v-for="item in currentConfig" :key="item.id"
					@click="configModule.expandContent(item.id, 'Email')">
					<p class="item-title">{{ item.title }}</p>
					<p class="email-date">————{{ Math.floor(item.email_date / 10000) }}年{{ Math.floor((item.emial_date %
						10000)
						/
						100) }}月{{ (item.email_date % 10000) % 100 }}日
					</p>
				</div>
				<p class="refresh-tip none-select" v-if="currentConfig.length !== 0" @click="getAllEmail">
					若缺少邮件<br>可尝试点击此处刷新界面( •̀ ω •́ )</p>
			</div>
		</div>
		<teleport class="fixed-page" to="#app #app-root">
			<Logo></Logo>
			<sidebar :type-list="emailTypeList" @change-dir="switchDirConfig"></sidebar>
			<div class="hidden-container" :style="{
				position:
					configModule.isContentExpanded ? 'absolute' : 'fixed'
			}">
				<div class="content-container" :style="{
					transform: configModule.isContentExpanded ?
						`translateY(calc(-120vh + ${du(-8)}))` : 'none'
				}">
					<button class="hide-content-button none-select" @click="configModule.hideContent()">×</button>
					<p class="content-title">{{ configModule.contentTitle }}</p>
					<div class="title-content-divider"></div>
					<p class="content-text">{{ configModule.contentText }}</p>
				</div>
			</div>
		</teleport>
	</div>

</template>

<script setup>
import api from "../utils/api"
import {
	classifyGroup, currentSidebarConfig, configModule, du
} from "../utils/index";
import { ref, onMounted, onUnmounted } from "vue"
import Sidebar from "../components/Sidebar.vue";
import Logo from "../components/Logo.vue";

const navList = ref([])
const currentConfig = ref([])
const groupMap = ref(new Map())
let isUnmounted = false

const emailTypeList = [
	{ index: 0, typeKey: "all", label: "所有", id: "all" },
	{ index: 1, typeKey: "offical", label: "官方", id: "offical" },
	{ index: 2, typeKey: "user", label: "用户", id: "user" },
	{ index: 3, typeKey: "recent", label: "较近", id: "recent" },
	{ index: 4, typeKey: "past", label: "较远", id: "past" }
]

async function getAllEmail() {
	const res = await api.post('/api/getAllEamil')
	if (isUnmounted) return

	const list = Array.isArray(res.data) ? res.data : []
	navList.value = list
	currentConfig.value = list
	groupMap.value = classifyGroup(list, 'type')
}

function switchDirConfig(sn, type) {
	currentSidebarConfig.value = sn

    switch (type) {
        case "all":
            currentConfig.value = navList.value
		    return
    
        case "recent":
            currentConfig.value = navList.value.reverse().slice(0,30)
            return

        case "past":
            currentConfig.value = navList.value.reverse().slice(30)
    }

	currentConfig.value = groupMap.value.get(type) ?? []
}

onMounted(async () => {
	currentSidebarConfig.value = 0
	await getAllAnnoInfo()
})

onUnmounted(() => {
	isUnmounted = true
})
</script>

<style scoped>
:root {
	/* 设计参考视高：457px；原 1vh = 4.57px */
	--design-vh: 4.57px;
	--design-width: 1096.8px;
	/* 457px * 2.4 */
}

.anno-date {
	width: 250px;
	text-align: left;
	position: absolute;
	right: 10%;
	top: 50%;
	font-size: calc(4 * var(--design-vh));
	color: #706048;
}

.item {
	height: calc(20 * var(--design-vh));
}
</style>
