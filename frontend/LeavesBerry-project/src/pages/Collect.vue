<template>
	<!--受到transform影响,不要把fixed,拖拽,需获取坐标的点击等放入-->
	<div class="page" id="collect-page">
		<div class="slide-page">
			<div class="item-box">
				<p class="no-item-tip none-select" v-if="currentConfig.length == 0" @click="getAllColl">暂无收藏( •̀ ω •́
					)✧<br>点击此处刷新</p>
				<div class="item" v-for="item in currentConfig" :key="item.id ?? item.url">
					<p class="item-title" @click="goPage(item.url)">
						{{ item.title ? item.title : '未知界面' }}</p>
					<div id="colls-function-box">
						<button id="discoll-button"
							@click.stop.prevent="cancelColl(`${item.url}`)"
							aria-label="取消收藏">
							<svg class="coll-function-icon" viewBox="0 0 24 24" aria-hidden="true"
							fill="currentColor" width="72" height="72">
								<path d="M12 2.8C12.8 7.8 16.2 11.2 21.2 12C16.2 12.8 12.8 16.2 12 21.2C11.2 16.2 7.8 12.8 2.8 12C7.8 11.2 11.2 7.8 12 2.8Z"
									></path>
							</svg>
						</button>
						<button @click.stop.prevent="createQRCode(`${ROOTPATH}${item.url}`)">
							<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="currentColor" 
								id="coll-qr-icon" style="transform: scale(0.5) translateX(-10%);">    
								<!-- 左上 -->
								<path fill-rule="evenodd" d="M0 0H15V15H0V0ZM3 3V12H12V3H3Z"/>
								<rect x="5" y="5" width="5" height="5"/>
								<!-- 右上 -->
								<path fill-rule="evenodd" d="M17 0H32V15H17V0ZM20 3V12H29V3H20Z"/>
								<rect x="22" y="5" width="5" height="5"/>  
								<!-- 左下 -->
								<path fill-rule="evenodd" d="M0 17H15V32H0V17ZM3 20V29H12V20H3Z"/>
								<rect x="5" y="22" width="5" height="5"/>
								<!-- 右下 -->
								<path fill-rule="evenodd" d="M17 17H32V32H17V17ZM20 20V29H29V20H20Z"/>
								<rect x="23" y="23" width="3" height="3"/>    
							</svg>
						</button>
							
						<button @click.stop.prevent="copyText(item.url)">
							<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" 
								id="share-link-icon" style="transform: scale(1.5) 
								translateY(8%) translateX(-10%);">
								<path d="M7.2 14.7 L4.9 17 C2.4 19.5 2.4 23.5 4.9 26 C7.4 28.5 11.4 28.5 13.9 26 L20.7 19.2 C23.2 16.7 23.2 12.7 20.7 10.2 C18.8 8.3 16 7.8 13.6 8.9"
								stroke="currentColor" stroke-width="3.4" stroke-linecap="square" stroke-linejoin="round"/>
								<path d="M11.4 17.8 C9.1 15.3 9.2 11.5 11.6 9.1 L17.8 2.9 C20.3 0.4 24.3 0.4 26.8 2.9 C29.3 5.4 29.3 9.4 26.8 11.9 L23.9 14.8"
								stroke="currentColor" stroke-width="3.4" stroke-linecap="square" stroke-linejoin="round"/>
								<path d="M18.1 24.7H29" stroke="currentColor" stroke-width="3.4" stroke-linecap="square"/>
							</svg>   
						</button>
					</div>
					<p class="item-desc" id="coll-desc">
                        |{{ item.desc ? item.desc : '未在本站详细注册的界面' }}</p>
				</div>
				<p class="refresh-tip none-select" v-if="currentConfig.length !== 0" @click="getAllColl">
					若缺少收藏<br>可尝试点击此处刷新界面( •̀ ω •́ )</p>
			</div>
		</div>
		<teleport class="fixed-page" to="#app #app-root">
			<Owner></Owner>
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
import Owner from "../components/Owner.vue";

let navList = []
let groupMap = new Map()
const currentConfig = ref([])
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
	navList = list
	groupMap = classifyGroup(list, 'type')

	const index = currentSidebarConfig.value
	
	
	if (index == 0) {
		currentConfig.value = navList
		return
	} 

	for (let item of collTypeList) {
		if (item.index == index) {
			currentConfig.value = groupMap.get(item.typeKey)
		}
	}
	
}

async function getAllColl() {
	if (!userState.isLogined) return

	if (isUnmounted) return

	const res = api.get('/api/getAllColl')

	applyCollList(res.data)
}

async function cancelColl(url) {
	if (!userState.isLogined) return

	const oldMap = groupMap
	const oldNavList = navList
	const oldConfig = currentConfig.value

	try {
		
		navList = navList.filter(item => item.url !== url)
		currentConfig.value = currentConfig.value.filter(item => item.url !== url)
		groupMap = classifyGroup(navList, 'type')

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
			navList = oldNavList
			currentConfig.value = oldConfig
			groupMap = oldConfig
		}
	}
	catch (e) {
		console.log(e)
		if (!isUnmounted) showTips(e)
		navList = oldNavList
		currentConfig.value = oldConfig
		groupMap = oldConfig
	}
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

.item button {
	width: calc(8 * var(--design-vh));
	height: calc(6 * var(--design-vh));
	background-color: rgba(0, 0, 0, 0);
	background-repeat: no-repeat;
	color: var(--secondary-color);
	margin-left: calc(1 * var(--design-vh));
	display: flex;
	justify-content: center;
	align-items: center;
	padding: 0;
	border-right: 1px solid var(--secondary-color);
	border-top: none;
	border-bottom: none;
	border-left: none;
	z-index: 4;
}

#discoll-button {
	color: var(--thirdary-color);
	border-left: 1px solid var(--secondary-color);
}

.coll-function-icon {
	transform: scale(1.3);
	display: block;
	width: calc(4 * var(--design-vh));
	height: calc(4 * var(--design-vh));
	flex: 0 0 calc(4 * var(--design-vh));
	pointer-events: none;
}

@media (min-width: 1px) and (orientation: portrait) {
	.item {
		height: calc(30 * var(--design-vh));
	}
	#colls-function-box {
		position: absolute;
		left: 6.4%;
		top: 65%;
	}
}

</style>
