<template>
	<div class="page" id="email-page">
		<div class="slide-page">
			<div class="item-box none-select" v-show="!configModule.isContentExpanded">
					<div class="item-box" v-if="currentContent == 'write'">
						<input id="main-text-input" v-model="mainTextInputValue" maxlength="1000">
						<input id="recipient-input" v-model="recipientInputValue">
						<button id="send-email-button" @click="sendEmail">⇦</button>
					</div>

					<div class="item-box" v-if="currentContent == 'recieve'">
						<p class="no-item-tip none-select" v-if="currentContent.length == 0" 
						@click="getAllEmailInfo">
							暂无邮件( •̀ ω •́ )✧<br>点击此处刷新</p>
						<div class="item" v-for="item in navList" :key="item.id"
							@click="configModule.expandContent(item.id, 'Email')">
							<p class="item-title">{{ item.title }}</p>
							<p class="email-date">————{{ Math.floor(item.email_date / 10000) }}年{{ Math.floor((item.emial_date %
								10000)
								/
								100) }}月{{ (item.email_date % 10000) % 100 }}日
							</p>
						</div>
						<p class="refresh-tip none-select" v-if="currentContent.length !== 0" @click="getAllEmailInfo">
							若缺少邮件<br>可尝试点击此处刷新界面( •̀ ω •́ )</p>
					</div>

				
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
					<p class="content-text" >{{ configModule.contentText }}</p>
				</div>
			</div>
		</teleport>
	</div>

</template>

<script setup>
import api from "../utils/api"
import {
	classifyGroup, currentSidebarConfig, configModule, du, userState
} from "../utils/index";
import { ref, onMounted, onUnmounted, watch } from "vue"
import Sidebar from "../components/Sidebar.vue";
import Logo from "../components/Logo.vue";

const navList = ref([])
const currentContent= ref('')
const groupMap = ref(new Map())

const mainTextInputValue = ref(null)
const recipientInputValue = ref(null)

let isUnmounted = false

const emailTypeList = [
	{ index: 0, typeKey: "write", label: "写信", id: "write" },
	{ index: 1, typeKey: "recieve", label: "收件", id: "recieve" }
]

async function getAllEmailInfo() {
	const res = await api.post('/api/getAllEamilInfo')
	if (isUnmounted) return

	const list = Array.isArray(res.data) ? res.data : []
	navList.value = list
	currentConfig.value = list
	groupMap.value = classifyGroup(list, 'type')
}

async function sendEmail() {
	if (!userState.isLogined || !mainText.value || !recipient.value) return

	if (recipientInputValue.value.length > 5 || !Number.isFinite(recipientInputValue.value)) {
		const reg = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
		const match = recipientInputValue.value.trim().match(reg)
		if (recipientInputValue.value.length > 40 || !match) {
			showTips("收件人格式错误")
			return
		}
	}
}

async function verifyEmail() {

	if (!configModule.contentText.length == 0) return

	const reg = /((https?|ftp|file):\/\/)?(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z0-9\-]+|(?:\d{1,3}\.){3}\d{1,3}(?:\/[\w.,@?^=%&:/~+#\-]*)*/g
	if (reg.test(configModule.contentText)) {
		let linkTypeList = ''
		if ([".com", ".cn", ".org"].some(char => configModule.contentText.include(char))){
			linkTypeList += " <第三方官方网站> "
		}
		if ([".top", ".xyz", ".club", ".win"].some(char => configModule.contentText.include(char))){
			linkTypeList += " <未认证的小型网站> "
		}
		if (configModule.contentText.include(".cc")) {
			linkTypeList += " <未认证的高危网站!!!> "
		}
		configModule.contentText += `\n\n该邮件中包含链接, 包括通向${linkTypeList}的链接, 请谨慎访问!`	
	}
}

function switchDirConfig(sn, type) {
	currentSidebarConfig.value = sn
    currentContent.value = type
}

watch(() => configModule.contentText, () => {
	verifyEmail()
})

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
