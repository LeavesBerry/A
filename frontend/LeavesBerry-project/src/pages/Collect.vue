<template>
	<!--受到transform影响,不要把fixed,拖拽,需获取坐标的点击等放入-->
	<div class="page" id="collect-page">
		<div class="slide-page">
			<div class="item-box">
				<p class="no-item-tip none-select" v-if="currentConfig.length == 0" @click="getAllColl">暂无收藏( •̀ ω •́
					)✧<br>点击此处刷新</p>
				<div class="item" v-for="item in currentConfig" :key="item.id ?? item.url">
					<p class="item-title" @click="goPage(item.url)">
						{{ item.title.length > 0 ? item.title : '未知界面' }}</p>
					<div id="colls-function-box">
						<button @click.stop.prevent="cancelColl(`${item.url}`)" style="color: #73B436; 
						font-size: calc(6 * var(--design-vh));
						padding-bottom: 2%;
						border-left: 1px solid #3A251A;">✦</button>
						<button @click.stop.prevent="createQRCode(`${ROOTPATH}${item.url}`)" style="background-image: url('/image/QR.png');
						background-size: calc(4 * var(--design-vh));
						background-position: calc(1.3 * var(--design-vh)) center;
						"></button>
						<button @click.stop.prevent="copyText(item.url)" style="background-image: url('/image/Link.png');
						background-size: calc(6 * var(--design-vh));
						background-position: calc(0.3 * var(--design-vh)) center;
						"></button>
					</div>
					<p id="coll-desc">
                        |{{ item.desc.length > 0 ? item.desc : '未在本站详细注册的界面' }}</p>
				</div>
				<p class="refresh-tip none-select" v-if="currentConfig.length !== 0" @click="getAllColl">
					若缺少收藏<br>可尝试点击此处刷新界面( •̀ ω •́ )</p>
			</div>
		</div>
		<teleport class="fixed-page" to="#app #app-root">
			<Logo></Logo>
			<sidebar :type-list="collTypeList" @change-dir="switchDirConfig"></sidebar>
		</teleport>
	</div>

</template>

<script setup>
import Sidebar from "../components/Sidebar.vue";
import api from "../utils/api"
import {
	userState, copyText, createQRCode, classifyGroup,
	currentSidebarConfig, showTips, useGoPage, apiRequest,
	disposeReturn
} from "../utils/index";
import { ROOTPATH } from "../router/index.js";
import { ref, onMounted, onUnmounted } from "vue"
import Logo from "../components/Logo.vue";

const navList = ref([])
const currentConfig = ref([])
const groupMap = ref(new Map())
const { goPage } = useGoPage()
let isUnmounted = false

const collTypeList = [
	{ index: 0, typeKey: "all", label: "所有", id: "all" },
	{ index: 1, typeKey: "essay", label: "文章", id: "essay" },
	{ index: 2, typeKey: "good", label: "商品", id: "good" },
	{ index: 3, typeKey: "music", label: "音乐", id: "music" },
	{ index: 4, typeKey: "other", label: "其他", id: "other" }
]

function applyCollList(data) {
	if (isUnmounted) return

	const list = Array.isArray(data) ? data : []
	navList.value = list
	currentConfig.value = list
	groupMap.value = classifyGroup(list, 'type')
}

async function getAllColl() {
	if (!userState.isLogined) return

	if (isUnmounted) return

	const coll_info = JSON.parse(localStorage.getItem('coll_info_cache'))

	applyCollList(coll_info)
	userState.isChangedColl = false
}

async function cancelColl(url) {
	if (!userState.isLogined) return

	const oldMap = groupMap.value
	const oldNavList = navList.value
	const oldConfig = currentConfig.value

	try {
		
		navList.value = navList.value.filter(item => item.url !== url)
		currentConfig.value = currentConfig.value.filter(item => item.url !== url)
		groupMap.value = classifyGroup(navList.value, 'type')

		const res = await apiRequest.toggleColl(url)
		if (isUnmounted) return

		if (!disposeReturn(res)) {
			let coll_info = JSON.parse(localStorage.getItem('coll_info_cache'))
            let coll_list = JSON.parse(localStorage.getItem('coll_list_cache'))
			const collIndex = coll_list.indexOf(url)
			coll_list.splice(collIndex)
			coll_info.splice(collIndex)
			localStorage.setItem('coll_list_cache', JSON.stringify(coll_list))
			localStorage.setItem('coll_info_cache', JSON.stringify(coll_info))
		}
		else {
			console.log(1)
			navList.value = oldNavList
			currentConfig.value = oldConfig
			groupMap.value = oldConfig
		}
	}
	catch (e) {
		console.log(e)
		if (!isUnmounted) showTips(e)
		navList.value = oldNavList
		currentConfig.value = oldConfig
		groupMap.value = oldConfig
	}
}

function switchDirConfig(sn, type) {
	currentSidebarConfig.value = sn

	if (type === "all") {
		currentConfig.value = navList.value
		return
	}

	currentConfig.value = groupMap.value.get(type) ?? []
}

onMounted(async () => {
	currentSidebarConfig.value = 0
	await getAllColl()
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

.item {
	height: calc(20 * var(--design-vh));
}

#colls-function-box {
	position: absolute;
	right: 10%;
	top: 15%;
	height: 10%;
	width: auto;
	display: flex;
	z-index: 3;
}

#coll-desc {
    width: fit-content;
    height: auto;
    font-size: calc(4 * var(--design-vh));
    color: #3A251A;
    font-weight: 400;
    position: absolute;
    top: 55%;
    left: 7%;
}

.item button {
	width: calc(8 * var(--design-vh));
	height: calc(6 * var(--design-vh));
	background-color: rgba(0, 0, 0, 0);
	background-repeat: no-repeat;
	color: #3A251A;
	margin-left: calc(1 * var(--design-vh));
	display: flex;
	justify-content: center;
	align-items: center;
	padding: 0;
	border-right: 1px solid #3A251A;
	border-top: none;
	border-bottom: none;
	border-left: none;
	z-index: 4;
}
</style>
