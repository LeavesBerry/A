<template>
	<div class="page" id="email-page">
		<div class="slide-page">
			<div class="item-box none-select" v-show="!configModule.isConfigClosed">
				<div v-if="currentContent == 'write'" class="item" id="write-email-box">
					<input id="email-title-input" v-model="emailTitleInputValue" maxlength="30"
					placeholder="请输入邮件标题 | 30字以内">
					<input id="recipient-input" v-model="recipientInputValue"
					placeholder="请输入收件人的ID或邮箱">
					<textarea id="main-text-input" v-model="mainTextInputValue" wrap="soft"
					maxlength="1000" placeholder="请输入邮件文本 | 1000字以内"></textarea>
					<button id="send-email-button" @click="sendEmail">发送邮件</button>
					<div id="tip-box">
						<p v-for="(item, index) in tipList" :key="`${index}-${item}`">•{{ item }}</p>
					</div>
				</div>

				<div v-if="currentContent == 'recieve'">
					<p class="no-item-tip none-select" v-if="currentConfig.length == 0" 
					@click="getAllEmailInfo">
						暂无邮件( •̀ ω •́ )✧<br>点击此处刷新</p>
					<div class="item" v-for="item in currentConfig" :key="item.id"
						@click="configModule.expandContent(item.id, 'Email')">
						<p class="item-title">{{ item.title }}</p>
						<p id="email-date">{{ Math.floor(item.email_date / 10000) }}年{{ Math.floor((item.email_date %
							10000)
							/
							100) }}月{{ (item.email_date % 10000) % 100 }}日
						</p>
						<p class="item-desc" id="email-desc">
							|{{ item.desc.length > 0 ? item.desc : '未在本站详细注册的界面' }}</p>
					</div>
					<p class="refresh-tip none-select" v-if="currentConfig.length !== 0" @click="getAllEmailInfo">
						若缺少邮件<br>可尝试点击此处刷新界面( •̀ ω •́ )</p>
				</div>

				<div v-if="currentContent == 'trash'">
					<p class="no-item-tip none-select" v-if="currentConfig.length == 0" 
					@click="getAllEmailInfo">
						暂无邮件( •̀ ω •́ )✧<br>点击此处刷新</p>
					<p class="refresh-tip none-select" v-if="currentConfig.length !== 0" @click="getAllEmailInfo">
						若缺少邮件<br>可尝试点击此处刷新界面( •̀ ω •́ )</p>
				</div>
				
			</div>
		</div>
		<teleport class="fixed-page" to="#app #app-root">
			<Owner></Owner>
			<Sidebar :type-list="emailTypeList" @change-dir="switchDirConfig"
			v-show="!configModule.isConfigClosed"></Sidebar>
			<ExContent></ExContent>
		</teleport>
	</div>

</template>

<script setup>
import api from "../utils/api"
import {
	classifyGroup, currentSidebarConfig, configModule, du, userState,
	apiRequest, useHashDetail,
	disposeReturn,
	showTips
} from "../utils/index";
import { ref, onMounted, onUnmounted, watch } from "vue"
import Sidebar from "../components/Sidebar.vue";
import Owner from "../components/Owner.vue";
import ExContent from "../components/ExContent.vue";

useHashDetail('Email')

let groupMap = new Map()
const currentContent= ref('write')
const currentConfig = ref([])


const mainTextInputValue = ref(null)
const recipientInputValue = ref(null)
const emailTitleInputValue = ref(null)

let isEmailVerifing = false

let isUnmounted = false

const emailTypeList = [
	{ index: 0, typeKey: "write", label: "写信", id: "write" },
	{ index: 1, typeKey: "recieve", label: "收件", id: "recieve" },
	{ index: 2, typeKey: "trash", label: "废件", id: "trash" }
]

const tipList = [
	"请友好交流,文明用语","发送邮件有30秒冷却","请勿暴露自己的隐私信息"
]

async function getAllEmailInfo() {
	const res = await api.post('/api/getAllEmailInfo')
	if (isUnmounted) return

	const list = Array.isArray(res.data) ? res.data : []
	groupMap = classifyGroup(list, "type")

	switch (currentContent) {
		case "recieve":
			currentConfig.value = groupMap.get("user") ?? []
			return

		case "trash":
			currentConfig.value = groupMap.get("blacker") ?? []
			return
	}
}

async function sendEmail() {
	if (!userState.isLogined || !mainTextInputValue.value || !recipientInputValue.value) return

	let res = null
	
	let re = recipientInputValue.value.trim()

	if (re.length > 40 || re.value == 0) {
		showTips("收件人格式错误")
		return
	}

	if (!isNaN(re) && re.length < 5) {
		try {
			re = Number(re)
			if (re == userState.userId) {
				showTips('你不能给自己发邮件QwQ')
				return
			}
		} catch(e) {
			showTips("收件人格式错误")
			showTips(e)
			return
		}

		res = apiRequest.sendEmail(re, null,
		mainTextInputValue.value, emailTitleInputValue.value)
		if(!disposeReturn(res)) {
			showTips(`成功将邮件发送给ID为${re}的用户`)
		}
	}
	else {
		if (re == userState.userEmail) {
			showTips('你不能给自己发邮件QwQ')
		}
		const reg = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
		const match = re.match(reg)
		if (match) {
			res = apiRequest.sendEmail(null, re, 
			mainTextInputValue.value, emailTitleInputValue.value)
			if(!disposeReturn(res)) {
				showTips(`成功将邮件发送给Email为${re}的用户`)
			}
		}
		else {
			showTips("收件人格式错误")
			return
		}
	}
}

async function verifyEmail() {

	if (configModule.contentText.length == 0) return

	isEmailVerifing = true

	const reg = /((https?|ftp|file):\/\/)?(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z0-9\-]+|(?:\d{1,3}\.){3}\d{1,3}(?:\/[\w.,@?^=%&:/~+#\-]*)*/
	
	if (reg.test(configModule.contentText)) {
		let linkTypeList = ''
		if ([".com", ".cn", ".org"].some(char => configModule.contentText.includes(char))){
			linkTypeList += " <第三方官方网站> "
		}
		else if ([".top", ".xyz", ".club", ".win"].some(char => configModule.contentText.includes(char))){
			linkTypeList += " <未认证的小型网站> "
		}
		else if (configModule.contentText.includes(".cc")) {
			linkTypeList += " <未认证的高危网站!!!> "
		}
		else {
			linkTypeList += " <非主流域名的网站> "
		}
		configModule.contentText = `该邮件中包含链接, 包括通向${linkTypeList}的链接, 请谨慎访问!\n\n` + 
		configModule.contentText
	}

	isEmailVerifing = false
	return
}

function switchDirConfig(sn, type) {
	currentSidebarConfig.value = sn
    currentContent.value = type

	switch (type) {
		case "recieve":
			currentConfig.value = groupMap.get("user") ?? []
			return

		case "trash":
			currentConfig.value = groupMap.get("blacker") ?? []
			return
	}

	currentConfig.value = []
}

watch(() => configModule.contentId, () => {
		verifyEmail()
})

onMounted(async () => {
	currentSidebarConfig.value = 0
	await getAllEmailInfo()
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

#email-date {
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

#email-title-input {
	width: 65vw;
	height: calc(8 * var(--design-vh));
	border-radius: calc(5 * var(--design-vh)) calc(5 * var(--design-vh)) 0 0;
	border: 3px solid var(--secondary-color);
	text-align: center;
	line-height: calc(8 * var(--design-vh));
	position: relative;
	margin-top: calc(6 * var(--design-vh));
	background: none;
	font-size: calc(4 * var(--design-vh));
	color: var(--secondary-color);
	font-weight: 600;
}

#email-title-input::placeholder {
	font-size: calc(4 * var(--design-vh));
	color: var(--secondary-color);
	font-weight: 600;
}

#recipient-input {
	width: 65vw;
	height: calc(8 * var(--design-vh));
	border-radius: 0 0 calc(5 * var(--design-vh)) calc(5 * var(--design-vh));
	border: 3px solid var(--secondary-color);
	text-align: center;
	line-height: calc(8 * var(--design-vh));
	position: relative;
	margin-top: -3px;
	background: none;
	font-size: calc(4 * var(--design-vh));
	color: var(--secondary-color);
}

#recipient-input::placeholder {
	font-size: calc(4 * var(--design-vh));
	color: var(--secondary-color);
	font-weight: 600;
}

#main-text-input {
	width: 65vw;
	height: fit-content;
	border-radius: calc(5 * var(--design-vh));
	border: 3px solid var(--secondary-color);
	text-align: left;
	padding: calc(1 * var(--design-vh)) 1% calc(1 * var(--design-vh)) 1%;
	position: relative;
	margin-top: calc(4 * var(--design-vh) - 3px);
	line-height: 1;
	background: none;
	font-size: calc(4 * var(--design-vh));
	color: var(--secondary-color);
	field-sizing: content;
    min-height: calc(10 * var(--design-vh, 4.57px));
    max-height: calc(300 * var(--design-vh, 4.57px));
    resize: none;
    overflow-y: hidden;
    background-color: rgba(0, 0, 0, 0);
    font-weight: 300;
    text-align: top;
    word-break: break-all;
    word-wrap: break-word;
    overflow-x: hidden;
}

#main-text-input::placeholder {
	font-size: calc(4 * var(--design-vh));
	color: var(--secondary-color);
	font-weight: 600;
}

#send-email-button {
	width: 65vw;
	height: calc(8 * var(--design-vh));
	border-radius: calc(5 * var(--design-vh));
	border: 3px solid var(--secondary-color);
	text-align: center;
	position: relative;
	top: calc(2 * var(--design-vh) - 3px);
	background: none;
	font-size: calc(4 * var(--design-vh));
	font-weight: 600;
	color: var(--secondary-color);
	cursor: pointer;
}

#tip-box {
	position: relative;
	margin-top: calc(4 * var(--design-vh));
	width: 65vw;
	height: auto;
	justify-items: left;
}

#tip-box p{
	color: #4a4030;
    font-size: 15px;
    font-weight: 500;
}

#write-email-box {
	min-height: calc(70 * var(--design-vh));
	flex-direction: column;
	height: max-content;
	display: flex;
	align-items: center;
	padding-bottom: calc(5 * var(--design-vh));
}

#write-email-box:active {
	transform: none;
}

@media (min-width: 1px) and (orientation: portrait) {
	.item {
		height: calc(30 * var(--design-vh));
	}
	#email-date {
		position: absolute;
		left: 7%;
		top: 65%;
	}
}
</style>
