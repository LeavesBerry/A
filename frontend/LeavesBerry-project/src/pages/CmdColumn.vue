<template>
	<div class="page" id="cmd-column-page">
		<div class="slide-page">
			<div class="item-box">
				<ExTextarea v-for="item in currentConfig" :key="item.id ?? item.cmd" :title="item.cmd" :text="item.des"
					custom-class="item" title-class="textarea-title" button-class="textarea-button"
					content-class="textarea-content">
				</ExTextarea>
				<p class="no-item-tip none-select" v-if="currentConfig.length == 0">暂无该类指令( •̀ ω •́ )✧</p>
				<!--直接用refresh-tip更方便-->
				<p class="refresh-tip none-select" v-if="currentConfig.length !== 0">更多指令,敬请期待( •̀ ω •́ )✧</p>
			</div>
		</div>
		<teleport class="fixed-page" to="#app #app-root">
			<Logo></Logo>
			<Sidebar :type-list="cmdTypeList" @change-dir="switchDirConfig"></Sidebar>
		</teleport>
	</div>

</template>

<script setup>
import Sidebar from '../components/Sidebar.vue';
import ExTextarea from '../components/ExTextarea.vue';
import { ref, onMounted, onUnmounted } from 'vue';
import {
	switchArrow, classifyGroup, arrowStyle,
	apiRequest, disposeReturn
} from '../utils/index';
import Logo from '../components/Logo.vue';

const navList = ref([])
const currentConfig = ref([])
const groupMap = ref(new Map())
let isUnmounted = false

const cmdTypeList = [
	{ index: 0, typeKey: "all", label: "所有", id: "all" },
	{ index: 1, typeKey: "route", label: "路由", id: "route" },
	{ index: 2, typeKey: "print", label: "打印", id: "print" },
	{ index: 3, typeKey: "test", label: "调试", id: "test" },
	{ index: 4, typeKey: "cache", label: "缓存", id: "cache" },
	{ index: 5, typeKey: "other", label: "其他", id: "other" }
]

function applyCmdList(data) {
	if (isUnmounted) return

	const list = Array.isArray(data) ? data : []
	navList.value = list
	currentConfig.value = list
	groupMap.value = classifyGroup(list, "type")
}

async function getCmdInfoList() {
	const cmdInfoCache = localStorage.getItem("cmd_info_cache")

	if (cmdInfoCache) {
		try {
			applyCmdList(JSON.parse(cmdInfoCache))
			return
		}
		catch {
			localStorage.removeItem("cmd_info_cache")
		}
	}

	const res = await apiRequest.getTextResourse("cmdInfoList")
	if (isUnmounted) return

	if (!disposeReturn(res)) {
		applyCmdList(res)
		localStorage.setItem("cmd_info_cache", JSON.stringify(navList.value))
	}
}

function switchDirConfig(sn, type) {
	switchArrow(sn)

	if (type === "all") {
		currentConfig.value = navList.value
		return
	}

	currentConfig.value = groupMap.value.get(type) ?? []
}

onMounted(async () => {
	arrowStyle.transform = ""
	await getCmdInfoList()
})

onUnmounted(() => {
	isUnmounted = true
})
</script>

<style>
#cmd-column-page .item {
	height: auto;
	flex-direction: column;
	padding-top: calc(1 * var(--design-vh));
	padding-bottom: calc(2 * var(--design-vh));
}

#cmd-column-page .textarea-title {
	width: fit-content;
	height: auto;
	font-size: calc(6 * var(--design-vh));
	color: #3A251A;
	font-weight: 800;
	position: relative;
	top: 0;
	left: 7%;
}

#cmd-column-page .textarea-button {
	position: absolute;
	right: 5%;
	top: calc(-2 * var(--design-vh));
	height: calc(10 * var(--design-vh));
	width: auto;
	background: none;
	border: none;
	font-size: calc(10 * var(--design-vh));
	font-weight: 500;
	color: #3A251A;
}

#cmd-column-page .textarea-content {
	position: relative;
	left: 7%;
	top: 8px;
	width: 86%;
	height: fit-content;
	padding-top: 1.5px;
	border-top: 1px solid #3A251A;
	color: #3A251A;
	text-align: left;
}
</style>
