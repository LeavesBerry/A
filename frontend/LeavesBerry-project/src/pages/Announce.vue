<template>
	<div class="page" id="announce-page">
		<div class="slide-page">
			<div class="item-box none-select" v-show="!configModule.isConfigClosed">
				<p class="no-item-tip none-select" v-if="currentConfig.length == 0" @click="getAllAnnoInfo">暂无公告( •̀ ω
					•́
					)✧<br>点击此处刷新</p>
				<div class="item" v-for="item in currentConfig" :key="item.id"
					@click="configModule.expandContent(item.id, 'Announce')">
					<p class="item-title">{{ item.title }}</p>
					<p id="anno-date">{{ Math.floor(item.anno_date / 10000) }}年{{ Math.floor((item.anno_date %
						10000)
						/
						100) }}月{{ (item.anno_date % 10000) % 100 }}日
					</p>
					<p class="item-desc" id="anno-desc">
                        |{{ item.desc.length > 0 ? item.desc : '未在本站详细注册的界面' }}</p>
				</div>
				<p class="refresh-tip none-select" v-if="currentConfig.length !== 0" @click="getAllAnnoInfo">
					若缺少公告<br>可尝试点击此处刷新界面( •̀ ω •́ )</p>
			</div>
		</div>
		<teleport class="fixed-page" to="#app #app-root">
			<Logo></Logo>
			<sidebar :type-list="annoTypeList" @change-dir="switchDirConfig"
			v-show="!configModule.isConfigClosed"></sidebar>
			<ExContent></ExContent>
		</teleport>
	</div>

</template>

<script setup>
import api from "../utils/api"
import {
	classifyGroup, currentSidebarConfig, configModule, du, useHashDetail
} from "../utils/index";
import { ref, onMounted, onUnmounted } from "vue"
import Sidebar from "../components/Sidebar.vue";
import Logo from "../components/Logo.vue";
import ExContent from "../components/ExContent.vue";

useHashDetail('Announce')

let navList = []
let groupMap = new Map()
const currentConfig = ref([])

let isUnmounted = false

const annoTypeList = [
	{ index: 0, typeKey: "all", label: "所有", id: "all" },
	{ index: 1, typeKey: "convention", label: "公约", id: "convention" },
	{ index: 2, typeKey: "update", label: "更新", id: "update" },
	{ index: 3, typeKey: "trailer", label: "预告", id: "trailer" },
	{ index: 4, typeKey: "other", label: "其他", id: "other" }
]

function applyAnnoList(data) {
	if (isUnmounted) return

	const list = Array.isArray(data) ? data : []
	navList = list
	groupMap = classifyGroup(list, 'type')

	const index = currentSidebarConfig.value

	if (index == 0) {
		currentConfig.value = navList
		return
	} 

	for (const item of annoTypeList) {
		if (item.index == index) {
			currentConfig.value = groupMap.get(item.typeKey)
		}
	}
	
	
}

async function getAllAnnoInfo() {
	const res = await api.post('/api/getAllAnnoInfo')
	if (isUnmounted) return

	applyAnnoList(res.data)
}

function switchDirConfig(sn, type) {
	currentSidebarConfig.value = sn

	if (type === "all") {
		currentConfig.value = navList
		return
	}

	currentConfig.value = groupMap.get(type) ?? []
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

#anno-date {
	width: 250px;
	text-align: left;
	position: absolute;
	right: 0;
	top: 50%;
	font-size: calc(4 * var(--design-vh));
	color: #706048;
}

.item {
	height: calc(20 * var(--design-vh));
}

@media (min-width: 1px) and (orientation: portrait) {
	.item {
		height: calc(30 * var(--design-vh));
	}
	#anno-date {
		position: absolute;
		left: 7%;
		top: 65%;
	}
}
</style>
